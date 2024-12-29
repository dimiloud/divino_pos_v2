from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from apps.inventory.models import Product

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('CASH', _('Espèces')),
        ('CARD', _('Carte')),
        ('TRANSFER', _('Virement')),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', _('En attente')),
        ('COMPLETED', _('Terminée')),
        ('CANCELLED', _('Annulée')),
        ('REFUNDED', _('Remboursée')),
    ]

    reference = models.CharField(_('Référence'), max_length=10, unique=True)
    cashier = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name=_('Caissier'),
        related_name='sales'
    )
    status = models.CharField(_('Status'), max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(_('Mode de paiement'), max_length=10, choices=PAYMENT_METHODS)
    subtotal = models.DecimalField(_('Sous-total'), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_('TVA'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)

    class Meta:
        verbose_name = _('Vente')
        verbose_name_plural = _('Ventes')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} ({self.get_status_display()})'

    @staticmethod
    def generate_reference():
        return get_random_string(10).upper()

    def calculate_totals(self):
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax = self.subtotal * 0.20  # 20% TVA
        self.total = self.subtotal + self.tax

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        self.calculate_totals()
        super().save(*args, **kwargs)

    @transaction.atomic
    def cancel(self):
        if self.status != 'COMPLETED':
            raise ValidationError(_('Seules les ventes terminées peuvent être annulées'))
        
        # Restaurer le stock
        for item in self.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
        
        self.status = 'CANCELLED'
        self.save()

class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        verbose_name=_('Vente'),
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('Produit'),
        related_name='sale_items'
    )
    quantity = models.PositiveIntegerField(_('Quantité'))
    unit_price = models.DecimalField(_('Prix unitaire'), max_digits=10, decimal_places=2)
    discount = models.DecimalField(_('Remise'), max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Détail de vente')
        verbose_name_plural = _('Détails de vente')

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': _('La quantité doit être supérieure à 0')})
        
        if self.product.stock_quantity < self.quantity:
            raise ValidationError({'quantity': _('Stock insuffisant')})

    def get_total(self):
        return (self.unit_price * self.quantity) - self.discount

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean()
        if not self.pk:  # Nouveau produit
            self.unit_price = self.product.price
            self.product.stock_quantity -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)
        self.sale.save()  # Recalculer les totaux