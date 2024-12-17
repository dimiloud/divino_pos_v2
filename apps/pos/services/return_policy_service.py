from django.utils import timezone
from datetime import timedelta
from ..models import ReturnPolicy, Return

class ReturnPolicyService:
    @staticmethod
    def validate_return(sale, items):
        """Vérifie si un retour est possible selon la politique en vigueur."""
        policy = ReturnPolicy.objects.filter(active=True).first()
        if not policy:
            raise ValueError('Aucune politique de retour active')

        # Vérifier le délai
        days_since_sale = (timezone.now().date() - sale.created_at.date()).days
        if days_since_sale > policy.days_limit:
            raise ValueError(
                f'Le délai de retour de {policy.days_limit} jours est dépassé'
            )

        # Vérifier les quantités retournées
        for item in items:
            original_item = sale.items.filter(
                product_variant=item['variant']
            ).first()

            if not original_item:
                raise ValueError(
                    f'Article {item["variant"]} non trouvé dans la vente'
                )

            returned_quantity = Return.objects.filter(
                sale=sale,
                product_variant=item['variant']
            ).aggregate(total=Sum('quantity'))['total'] or 0

            if returned_quantity + item['quantity'] > original_item.quantity:
                raise ValueError(
                    f'Quantité de retour supérieure à la quantité achetée'
                )

        return True

    @staticmethod
    def calculate_refund_amount(return_item):
        """Calcule le montant du remboursement selon la politique."""
        policy = ReturnPolicy.objects.filter(active=True).first()
        if not policy:
            raise ValueError('Aucune politique de retour active')

        original_price = return_item.product_variant.product.base_price
        quantity = return_item.quantity
        subtotal = original_price * quantity

        # Appliquer les frais de restockage si nécessaire
        days_since_sale = (timezone.now().date() - return_item.sale.created_at.date()).days
        if days_since_sale > policy.exchange_only_after_days:
            restocking_fee = subtotal * (policy.restocking_fee_percentage / 100)
            subtotal -= restocking_fee

        return subtotal