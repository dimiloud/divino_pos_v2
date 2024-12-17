from decimal import Decimal
from django.utils import timezone
from .models import Product, ProductVariant, Discount

class PriceService:
    @staticmethod
    def calculate_product_price(product, quantity=1):
        """Calcule le prix d'un produit en tenant compte des promotions actives."""
        base_price = product.base_price
        active_discounts = Discount.objects.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
            active=True
        ).filter(
            models.Q(products=product) |
            models.Q(categories=product.category) |
            models.Q(collections=product.collection)
        ).distinct()

        # Appliquer la meilleure réduction
        max_discount = Decimal('0')
        for discount in active_discounts:
            if discount.discount_type == 'percentage':
                current_discount = base_price * (discount.value / 100)
            else:
                current_discount = discount.value

            max_discount = max(max_discount, current_discount)

        final_price = base_price - max_discount
        return max(final_price, Decimal('0')) * quantity

    @staticmethod
    def get_active_promotions():
        """Récupère toutes les promotions actives."""
        return Discount.objects.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
            active=True
        )

    @staticmethod
    def apply_bulk_discount(products, discount):
        """Applique une réduction à plusieurs produits."""
        success_count = 0
        for product in products:
            try:
                if discount.discount_type == 'percentage':
                    new_price = product.base_price * (1 - discount.value / 100)
                else:
                    new_price = product.base_price - discount.value

                product.base_price = max(new_price, Decimal('0'))
                product.save()
                success_count += 1
            except Exception as e:
                print(f"Erreur lors de l'application de la réduction pour {product}: {str(e)}")

        return success_count