from django.db import models
from apps.core.models import TimeStampedModel
from django.core.validators import MinValueValidator

class StockMovement(TimeStampedModel):
    MOVEMENT_TYPES = [
        ('in', 'Entrée'),
        ('out', 'Sortie'),
        ('adjustment', 'Ajustement'),
    ]

    product = models.ForeignKey('pos.Product', on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    reference = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.movement_type == 'in':
            self.product.stock_quantity += self.quantity
        elif self.movement_type == 'out':
            self.product.stock_quantity -= self.quantity
        elif self.movement_type == 'adjustment':
            self.product.stock_quantity = self.quantity

        self.product.save()
        super().save(*args, **kwargs)

class StockAlert(TimeStampedModel):
    ALERT_TYPES = [
        ('low_stock', 'Stock bas'),
        ('out_of_stock', 'Rupture de stock'),
        ('expired', 'Périmé'),
    ]

    product = models.ForeignKey('pos.Product', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.get_alert_type_display()} - {self.product.name}'