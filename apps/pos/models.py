from django.db import models
from django.conf import settings

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Espèces'),
        ('CARD', 'Carte'),
        ('MOBILE', 'Paiement mobile')
    ]
    
    reference = models.CharField(max_length=20, unique=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.reference

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_total(self):
        return self.quantity * self.unit_price