from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum
from ..models import ReturnPolicy, Return, Sale, ProductVariant, Size, Color, Product
from ..services.return_policy_service import ReturnPolicyService

class ReturnPolicyServiceTestCase(TestCase):
    def setUp(self):
        # Créer une politique de retour
        self.policy = ReturnPolicy.objects.create(
            days_limit=30,
            receipt_required=True,
            original_tags_required=True,
            unworn_condition_required=True,
            restocking_fee_percentage=Decimal('10.00'),
            exchange_only_after_days=14,
            active=True
        )

        # Créer un produit et une variante
        self.product = Product.objects.create(
            name='Test Product',
            base_price=Decimal('100.00'),
            reference='TEST-001'
        )

        self.size = Size.objects.create(name='M', order=2)
        self.color = Color.objects.create(name='Black', code='#000000')

        self.variant = ProductVariant.objects.create(
            product=self.product,
            size=self.size,
            color=self.color,
            stock_quantity=10,
            sku='TEST-001-M'
        )

        # Créer une vente
        self.sale = Sale.objects.create(
            reference='SALE-001',
            total_amount=Decimal('100.00'),
            payment_method='cash',
            created_at=timezone.now() - timedelta(days=10)
        )

    def test_validate_return_within_time_limit(self):
        items = [{
            'variant': self.variant,
            'quantity': 1
        }]

        # Le retour est dans la limite de temps
        self.assertTrue(ReturnPolicyService.validate_return(self.sale, items))

    def test_validate_return_past_time_limit(self):
        self.sale.created_at = timezone.now() - timedelta(days=40)
        self.sale.save()

        items = [{
            'variant': self.variant,
            'quantity': 1
        }]

        # Le retour est hors délai
        with self.assertRaises(ValueError) as context:
            ReturnPolicyService.validate_return(self.sale, items)
        
        self.assertIn('délai de retour', str(context.exception))

    def test_validate_return_quantity(self):
        # Créer un retour existant
        Return.objects.create(
            sale=self.sale,
            product_variant=self.variant,
            quantity=1,
            reason='size'
        )

        items = [{
            'variant': self.variant,
            'quantity': 2  # Tenter de retourner plus que la quantité achetée
        }]

        with self.assertRaises(ValueError) as context:
            ReturnPolicyService.validate_return(self.sale, items)
        
        self.assertIn('Quantité', str(context.exception))

    def test_calculate_refund_amount_with_restocking_fee(self):
        return_item = Return.objects.create(
            sale=self.sale,
            product_variant=self.variant,
            quantity=1,
            reason='size'
        )

        # La vente a plus de 14 jours, donc des frais de restockage s'appliquent
        self.sale.created_at = timezone.now() - timedelta(days=20)
        self.sale.save()

        amount = ReturnPolicyService.calculate_refund_amount(return_item)
        expected_amount = Decimal('90.00')  # 100 - 10% de frais
        self.assertEqual(amount, expected_amount)

    def test_calculate_refund_amount_without_restocking_fee(self):
        return_item = Return.objects.create(
            sale=self.sale,
            product_variant=self.variant,
            quantity=1,
            reason='size'
        )

        # La vente a moins de 14 jours, pas de frais de restockage
        self.sale.created_at = timezone.now() - timedelta(days=7)
        self.sale.save()

        amount = ReturnPolicyService.calculate_refund_amount(return_item)
        expected_amount = Decimal('100.00')
        self.assertEqual(amount, expected_amount)

    def test_multiple_items_return(self):
        items = [{
            'variant': self.variant,
            'quantity': 1
        }]

        # Premier retour réussi
        self.assertTrue(ReturnPolicyService.validate_return(self.sale, items))

        # Créer le retour
        Return.objects.create(
            sale=self.sale,
            product_variant=self.variant,
            quantity=1,
            reason='size'
        )

        # Tenter un deuxième retour
        with self.assertRaises(ValueError):
            ReturnPolicyService.validate_return(self.sale, items)

    def test_no_active_policy(self):
        # Désactiver la politique de retour
        self.policy.active = False
        self.policy.save()

        items = [{
            'variant': self.variant,
            'quantity': 1
        }]

        with self.assertRaises(ValueError) as context:
            ReturnPolicyService.validate_return(self.sale, items)
        
        self.assertIn('Aucune politique de retour active', str(context.exception))