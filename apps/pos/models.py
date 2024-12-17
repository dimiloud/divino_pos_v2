from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel

class Return(TimeStampedModel):
    RETURN_STATUS = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Refusé'),
        ('completed', 'Terminé')
    ]

    sale = models.ForeignKey('Sale', on_delete=models.PROTECT)
    product_variant = models.ForeignKey('inventory.ProductVariant', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    reason = models.CharField(max_length=20, choices=[
        ('size', 'Taille incorrecte'),
        ('color', 'Couleur ne convient pas'),
        ('quality', 'Problème de qualité'),
        ('change_mind', 'Changement d\'avis'),
        ('other', 'Autre raison')
    ])
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=RETURN_STATUS, default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    processed_date = models.DateTimeField(null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def approve(self, user):
        if self.status == 'pending':
            self.status = 'approved'
            self.processed_by = user
            self.processed_date = timezone.now()
            self.save()
            
            # Mettre à jour le stock
            self.product_variant.stock_quantity += self.quantity
            self.product_variant.save()

    def reject(self, user, reason=''):
        if self.status == 'pending':
            self.status = 'rejected'
            self.processed_by = user
            self.processed_date = timezone.now()
            self.description = f"Rejeté: {reason}"
            self.save()

class Exchange(TimeStampedModel):
    EXCHANGE_STATUS = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé')
    ]

    return_item = models.OneToOneField(Return, on_delete=models.PROTECT)
    new_variant = models.ForeignKey('inventory.ProductVariant', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=EXCHANGE_STATUS, default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    processed_date = models.DateTimeField(null=True)
    price_difference = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_received = models.BooleanField(default=False)

    def process(self, user):
        if self.status == 'pending':
            # Vérifier le stock disponible
            if self.new_variant.stock_quantity >= self.return_item.quantity:
                # Mettre à jour les stocks
                self.new_variant.stock_quantity -= self.return_item.quantity
                self.new_variant.save()
                
                self.status = 'completed'
                self.processed_by = user
                self.processed_date = timezone.now()
                self.save()
                
                # Mettre à jour le statut du retour
                self.return_item.status = 'completed'
                self.return_item.save()
                
                return True
        return False

class ReturnReason(models.Model):
    name = models.CharField(max_length=100)
    requires_inspection = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ReturnPolicy(models.Model):
    days_limit = models.PositiveIntegerField(default=30)
    receipt_required = models.BooleanField(default=True)
    original_tags_required = models.BooleanField(default=True)
    unworn_condition_required = models.BooleanField(default=True)
    restocking_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exchange_only_after_days = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Return Policies'

    def is_return_allowed(self, sale):
        if not self.active:
            return False
            
        days_since_sale = (timezone.now().date() - sale.created_at.date()).days
        return days_since_sale <= self.days_limit