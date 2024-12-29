from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from apps.inventory.models import Product

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Espèces'),
        ('CARD', 'Carte'),
    ]
    
    reference = models.CharField(max_length=10, unique=True)
    cashier = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_reference():
        return get_random_string(10).upper()