from django.db.models import Count, Sum, Avg, F, Q, Case, When, Value, IntegerField
from django.db.models.functions import TruncMonth, ExtractWeekDay
from django.utils import timezone
from datetime import timedelta
from ..models import Return, Exchange, ProductVariant

class ReturnAnalyticsService:
    @staticmethod
    def get_return_statistics(start_date=None, end_date=None):
        """Obtient des statistiques globales sur les retours."""
        queryset = Return.objects.all()

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        stats = queryset.aggregate(
            total_returns=Count('id'),
            approved_returns=Count('id', filter=Q(status='approved')),
            rejected_returns=Count('id', filter=Q(status='rejected')),
            total_refund_amount=Sum('refund_amount'),
            avg_refund_amount=Avg('refund_amount'),
            exchange_rate=Count('exchange') * 100.0 / Count('id')
        )

        # Raisons des retours
        reasons = queryset.values('reason').annotate(
            count=Count('id'),
            percentage=Count('id') * 100.0 / queryset.count()
        ).order_by('-count')

        stats['return_reasons'] = list(reasons)
        return stats

    @staticmethod
    def get_size_exchange_patterns():
        """Analyse les motifs d'échange de tailles."""
        exchanges = Exchange.objects.filter(
            return_item__reason='size'
        ).select_related(
            'return_item__product_variant__size',
            'new_variant__size'
        )

        patterns = exchanges.values(
            'return_item__product_variant__size__name',
            'new_variant__size__name'
        ).annotate(
            count=Count('id'),
            percentage=Count('id') * 100.0 / exchanges.count()
        ).order_by('-count')

        return list(patterns)

    @staticmethod
    def get_product_return_rates():
        """Calcule les taux de retour par produit."""
        return ProductVariant.objects.annotate(
            total_sales=Count('saleitems'),
            total_returns=Count('returns'),
            return_rate=Case(
                When(total_sales__gt=0,
                     then=F('total_returns') * 100.0 / F('total_sales')),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).select_related(
            'product', 'size', 'color'
        ).filter(
            total_sales__gt=0
        ).order_by('-return_rate')

    @staticmethod
    def get_return_trends():
        """Analyse les tendances de retour sur le temps."""
        last_12_months = timezone.now() - timedelta(days=365)

        monthly_returns = Return.objects.filter(
            created_at__gte=last_12_months
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_returns=Count('id'),
            approved_returns=Count('id', filter=Q(status='approved')),
            rejected_returns=Count('id', filter=Q(status='rejected')),
            exchange_count=Count('exchange'),
            avg_refund=Avg('refund_amount')
        ).order_by('month')

        return list(monthly_returns)

    @staticmethod
    def get_customer_return_behavior():
        """Analyse le comportement de retour des clients."""
        return Return.objects.values(
            'sale__customer'
        ).annotate(
            return_count=Count('id'),
            total_amount=Sum('refund_amount'),
            exchange_rate=Count('exchange') * 100.0 / Count('id'),
            avg_processing_time=Avg(
                F('processed_date') - F('created_at'),
                filter=Q(processed_date__isnull=False)
            )
        ).filter(
            return_count__gt=1
        ).order_by('-return_count')

    @staticmethod
    def get_return_impact_on_inventory():
        """Analyse l'impact des retours sur l'inventaire."""
        return ProductVariant.objects.annotate(
            initial_stock=F('stock_quantity') + Sum(
                Case(
                    When(returns__status='approved',
                         then=-F('returns__quantity')),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ),
            returned_stock=Sum(
                Case(
                    When(returns__status='approved',
                         then=F('returns__quantity')),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ),
            return_impact_percentage=Case(
                When(initial_stock__gt=0,
                     then=F('returned_stock') * 100.0 / F('initial_stock')),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).select_related(
            'product', 'size', 'color'
        ).filter(
            initial_stock__gt=0
        ).order_by('-return_impact_percentage')