from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from decimal import Decimal

class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_margin(self):
        return (self.price - self.cost) / self.price * 100

class Sale(TimeStampedModel):
    PAYMENT_METHODS = [
        ('cash', 'Espèces'),
        ('card', 'Carte'),
        ('transfer', 'Virement'),
    ]

    reference = models.CharField(max_length=50, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('completed', 'Complété'),
            ('cancelled', 'Annulé'),
        ],
        default='pending'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.reference} - {self.total_amount}€'

class SaleItem(TimeStampedModel):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price * (1 - self.discount / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'