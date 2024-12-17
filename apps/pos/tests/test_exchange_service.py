from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from ..models import Return, Exchange, Product, ProductVariant, Sale, Size, Color
from ..services.exchange_service import ExchangeService

class ExchangeServiceTestCase(TestCase):
    def setUp(self):
        # Créer les données de test
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Créer un produit avec deux variantes
        self.product = Product.objects.create(
            name='Test Product',
            base_price=Decimal('100.00'),
            reference='TEST-001'
        )
        
        self.size_m = Size.objects.create(name='M', order=2)
        self.size_l = Size.objects.create(name='L', order=3)
        self.color = Color.objects.create(name='Black', code='#000000')

        self.variant_m = ProductVariant.objects.create(
            product=self.product,
            size=self.size_m,
            color=self.color,
            stock_quantity=10,
            sku='TEST-001-M'
        )

        self.variant_l = ProductVariant.objects.create(
            product=self.product,
            size=self.size_l,
            color=self.color,
            stock_quantity=5,
            sku='TEST-001-L'
        )

        # Créer une vente et un retour
        self.sale = Sale.objects.create(
            reference='SALE-001',
            total_amount=Decimal('100.00'),
            payment_method='cash'
        )

        self.return_item = Return.objects.create(
            sale=self.sale,
            product_variant=self.variant_m,
            quantity=1,
            reason='size',
            status='approved'
        )

    def test_process_exchange_success(self):
        # Créer un échange
        exchange = Exchange.objects.create(
            return_item=self.return_item,
            new_variant=self.variant_l
        )

        # Traiter l'échange
        processed_exchange = ExchangeService.process_exchange(exchange.id, self.user)

        # Vérifier le statut
        self.assertEqual(processed_exchange.status, 'completed')
        self.assertEqual(processed_exchange.return_item.status, 'completed')

        # Vérifier les stocks
        self.variant_m.refresh_from_db()
        self.variant_l.refresh_from_db()
        self.assertEqual(self.variant_m.stock_quantity, 11)  # +1 retourné
        self.assertEqual(self.variant_l.stock_quantity, 4)   # -1 échangé

    def test_exchange_invalid_stock(self):
        # Mettre le stock à 0
        self.variant_l.stock_quantity = 0
        self.variant_l.save()

        exchange = Exchange.objects.create(
            return_item=self.return_item,
            new_variant=self.variant_l
        )

        # Vérifier que l'échange est refusé
        with self.assertRaises(ValueError):
            ExchangeService.process_exchange(exchange.id, self.user)

    def test_price_difference_calculation(self):
        # Modifier le prix du nouvel article
        self.product.base_price = Decimal('120.00')
        self.product.save()

        difference = ExchangeService.calculate_price_difference(
            self.return_item,
            self.variant_l
        )

        self.assertEqual(difference, Decimal('20.00'))

    def test_validate_exchange(self):
        # Test avec un retour valide
        self.assertTrue(
            ExchangeService.validate_exchange(self.return_item, self.variant_l)
        )

        # Test avec un retour déjà échangé
        Exchange.objects.create(
            return_item=self.return_item,
            new_variant=self.variant_l
        )

        with self.assertRaises(ValueError):
            ExchangeService.validate_exchange(self.return_item, self.variant_l)

    def test_get_available_variants(self):
        variants = ExchangeService.get_available_variants(self.return_item)
        
        # Devrait retourner uniquement la variante L
        self.assertEqual(variants.count(), 1)
        self.assertEqual(variants.first(), self.variant_l)