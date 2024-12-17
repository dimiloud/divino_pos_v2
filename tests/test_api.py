from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.pos.models import Product, Category, Sale
from decimal import Decimal

class ProductAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=Decimal('10.00'),
            cost=Decimal('5.00'),
            stock_quantity=50
        )

    def test_get_products(self):
        url = reverse('api:product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product(self):
        url = reverse('api:product-list')
        data = {
            'name': 'New Product',
            'category': self.category.id,
            'price': '15.00',
            'cost': '7.50',
            'stock_quantity': 100
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class SaleAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=Decimal('10.00'),
            cost=Decimal('5.00'),
            stock_quantity=50
        )

    def test_create_sale(self):
        url = reverse('api:sale-list')
        data = {
            'payment_method': 'cash',
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 2,
                    'unit_price': '10.00'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que le stock a été mis à jour
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 48)