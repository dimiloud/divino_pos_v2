from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_('Nom'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    active = models.BooleanField(_('Actif'), default=True)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)

    class Meta:
        verbose_name = _('Catégorie')
        verbose_name_plural = _('Catégories')
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(_('Nom'), max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name=_('Catégorie'),
        related_name='products'
    )
    description = models.TextField(_('Description'), blank=True)
    price = models.DecimalField(_('Prix'), max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(_('Quantité en stock'), default=0)
    minimum_stock = models.IntegerField(_('Stock minimum'), default=5)
    barcode = models.CharField(_('Code-barres'), max_length=50, blank=True, null=True, unique=True)
    active = models.BooleanField(_('Actif'), default=True)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)

    class Meta:
        verbose_name = _('Produit')
        verbose_name_plural = _('Produits')
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        if self.stock_quantity < 0:
            raise ValidationError({'stock_quantity': _('La quantité en stock ne peut pas être négative')})

    def is_low_stock(self):
        return self.stock_quantity <= self.minimum_stock

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', _('Entrée')),
        ('OUT', _('Sortie')),
        ('ADJUST', _('Ajustement')),
        ('RETURN', _('Retour')),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('Produit'),
        related_name='stock_movements'
    )
    quantity = models.IntegerField(_('Quantité'))
    movement_type = models.CharField(_('Type'), max_length=10, choices=MOVEMENT_TYPES)
    notes = models.TextField(_('Notes'), blank=True)
    reference = models.CharField(_('Référence'), max_length=50, blank=True)
    created_at = models.DateTimeField(_('Date'), auto_now_add=True)

    class Meta:
        verbose_name = _('Mouvement de stock')
        verbose_name_plural = _('Mouvements de stock')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.movement_type == 'OUT' and self.quantity > self.product.stock_quantity:
            raise ValidationError(_('Stock insuffisant'))
        
        # Mise à jour du stock
        if self.movement_type in ['IN', 'RETURN']:
            self.product.stock_quantity += self.quantity
        elif self.movement_type == 'OUT':
            self.product.stock_quantity -= self.quantity
        elif self.movement_type == 'ADJUST':
            self.product.stock_quantity = self.quantity
        
        self.product.save()
        super().save(*args, **kwargs)