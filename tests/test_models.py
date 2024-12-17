from django.test import TestCase
from django.contrib.auth.models import User
from apps.pos.models import Product, Category, Sale, SaleItem
from apps.inventory.models import StockMovement
from decimal import Decimal

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=Decimal('10.00'),
            cost=Decimal('5.00'),
            stock_quantity=50
        )

    def test_product_margin(self):
        self.assertEqual(self.product.get_margin(), Decimal('50.00'))

    def test_stock_update(self):
        initial_stock = self.product.stock_quantity
        movement = StockMovement.objects.create(
            product=self.product,
            movement_type='in',
            quantity=10
        )
        self.product.refresh_from_db()
        self.assertEqual(
            self.product.stock_quantity,
            initial_stock + 10
        )

class SaleModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=Decimal('10.00'),
            cost=Decimal('5.00'),
            stock_quantity=50
        )

    def test_sale_creation(self):
        sale = Sale.objects.create(
            cashier=self.user,
            payment_method='cash',
            total_amount=Decimal('20.00')
        )
        item = SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=2,
            unit_price=Decimal('10.00'),
            total_price=Decimal('20.00')
        )
        
        self.assertEqual(sale.items.count(), 1)
        self.assertEqual(sale.total_amount, Decimal('20.00'))
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 48)