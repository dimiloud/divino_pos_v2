from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import Return, Exchange, StockMovement

class ExchangeService:
    @staticmethod
    @transaction.atomic
    def process_exchange(exchange_id, user):
        """Traite un échange en mettant à jour les stocks et les statuts."""
        exchange = Exchange.objects.select_related(
            'return_item__product_variant',
            'new_variant'
        ).get(id=exchange_id)

        # Vérifier que l'échange est en attente
        if exchange.status != 'pending':
            raise ValueError('Cet échange ne peut plus être traité')

        # Vérifier le stock disponible
        if exchange.new_variant.stock_quantity < exchange.return_item.quantity:
            raise ValueError('Stock insuffisant pour l\'échange')

        # Décrémenter le stock du nouvel article
        exchange.new_variant.stock_quantity -= exchange.return_item.quantity
        exchange.new_variant.save()

        # Créer les mouvements de stock
        StockMovement.objects.create(
            product_variant=exchange.return_item.product_variant,
            quantity=exchange.return_item.quantity,
            movement_type='in',
            reference=f'EXCH-{exchange.id}-IN',
            description=f'Échange #{exchange.id} - Retour'
        )

        StockMovement.objects.create(
            product_variant=exchange.new_variant,
            quantity=exchange.return_item.quantity,
            movement_type='out',
            reference=f'EXCH-{exchange.id}-OUT',
            description=f'Échange #{exchange.id} - Sortie'
        )

        # Mettre à jour le statut de l'échange
        exchange.status = 'completed'
        exchange.processed_by = user
        exchange.processed_date = timezone.now()
        exchange.save()

        # Mettre à jour le statut du retour
        return_item = exchange.return_item
        return_item.status = 'completed'
        return_item.processed_date = timezone.now()
        return_item.save()

        return exchange

    @staticmethod
    def calculate_price_difference(return_item, new_variant):
        """Calcule la différence de prix entre l'article retourné et le nouvel article."""
        original_price = return_item.product_variant.product.base_price
        new_price = new_variant.product.base_price

        return (new_price - original_price) * return_item.quantity

    @staticmethod
    def validate_exchange(return_item, new_variant):
        """Valide si un échange est possible."""
        # Vérifier que le retour est approuvé
        if return_item.status != 'approved':
            raise ValueError('Le retour doit être approuvé pour effectuer un échange')

        # Vérifier que l'article n'a pas déjà été échangé
        if hasattr(return_item, 'exchange'):
            raise ValueError('Cet article a déjà été échangé')

        # Vérifier le stock disponible
        if new_variant.stock_quantity < return_item.quantity:
            raise ValueError('Stock insuffisant pour le nouvel article')

        return True

    @staticmethod
    def get_available_variants(return_item):
        """Retourne les variantes disponibles pour l'échange."""
        product = return_item.product_variant.product
        
        return product.variants.exclude(
            id=return_item.product_variant.id
        ).filter(
            stock_quantity__gte=return_item.quantity
        ).select_related('size', 'color')