from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncMonth, ExtractWeekDay
from django.utils import timezone
from datetime import timedelta
from apps.pos.models import Sale, SaleItem
from apps.inventory.models import Product, ProductVariant, Collection

class SalesAnalyticsService:
    @staticmethod
    def get_collection_performance(collection_id):
        collection = Collection.objects.get(pk=collection_id)
        size_performance = (
            SaleItem.objects
            .filter(
                product__collection=collection,
                product_variant__size__isnull=False
            )
            .values('product_variant__size__name')
            .annotate(
                total_sales=Sum('total_price'),
                units_sold=Sum('quantity')
            )
            .order_by('-units_sold')
        )

        color_performance = (
            SaleItem.objects
            .filter(
                product__collection=collection,
                product_variant__color__isnull=False
            )
            .values('product_variant__color__name')
            .annotate(
                total_sales=Sum('total_price'),
                units_sold=Sum('quantity')
            )
            .order_by('-units_sold')
        )

        return {
            'size_performance': size_performance,
            'color_performance': color_performance
        }

    @staticmethod
    def get_bestsellers(days=30, limit=10):
        """Identifie les meilleurs vendeurs sur une période donnée."""
        start_date = timezone.now() - timedelta(days=days)
        
        return (
            SaleItem.objects
            .filter(
                sale__created_at__gte=start_date,
                sale__payment_status='completed'
            )
            .values(
                'product__name',
                'product__reference',
                'product_variant__size__name',
                'product_variant__color__name'
            )
            .annotate(
                total_sales=Sum('total_price'),
                units_sold=Sum('quantity'),
                avg_price=Avg('unit_price')
            )
            .order_by('-units_sold')[:limit]
        )

    @staticmethod
    def get_inventory_value():
        """Calcule la valeur totale du stock."""
        return (
            ProductVariant.objects
            .aggregate(
                total_value=Sum(F('stock_quantity') * F('product__cost')),
                total_retail_value=Sum(F('stock_quantity') * F('product__base_price'))
            )
        )

    @staticmethod
    def get_sales_by_hour():
        """Analyse les ventes par heure pour identifier les pics d'activité."""
        return (
            Sale.objects
            .filter(payment_status='completed')
            .annotate(hour=ExtractHour('created_at'))
            .values('hour')
            .annotate(
                total_sales=Sum('total_amount'),
                num_transactions=Count('id')
            )
            .order_by('hour')
        )

class InventoryAnalyticsService:
    @staticmethod
    def get_stock_turnover(days=30):
        """Calcule le taux de rotation du stock par produit."""
        start_date = timezone.now() - timedelta(days=days)
        
        return (
            Product.objects
            .annotate(
                sold_quantity=Sum(
                    'variants__saleitems__quantity',
                    filter=models.Q(variants__saleitems__sale__created_at__gte=start_date)
                ),
                avg_stock=Avg('variants__stock_quantity')
            )
            .annotate(
                turnover_rate=F('sold_quantity') / F('avg_stock')
            )
            .order_by('-turnover_rate')
        )

    @staticmethod
    def get_low_performing_items(threshold_days=90):
        """Identifie les articles avec peu ou pas de ventes."""
        threshold_date = timezone.now() - timedelta(days=threshold_days)
        
        return (
            Product.objects
            .annotate(
                last_sale=Max('variants__saleitems__sale__created_at'),
                total_sales=Count('variants__saleitems')
            )
            .filter(
                models.Q(last_sale__lt=threshold_date) |
                models.Q(last_sale__isnull=True)
            )
            .order_by('last_sale')
        )