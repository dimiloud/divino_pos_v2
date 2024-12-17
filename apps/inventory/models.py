from django.db import models
from apps.core.models import TimeStampedModel

class Size(models.Model):
    name = models.CharField(max_length=10)  # XS, S, M, L, XL, etc.
    description = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)  # Pour trier les tailles

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']

class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=7)  # Code hexadécimal
    
    def __str__(self):
        return self.name

class Collection(TimeStampedModel):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=20, choices=[
        ('spring', 'Printemps'),
        ('summer', 'Été'),
        ('fall', 'Automne'),
        ('winter', 'Hiver')
    ])
    year = models.IntegerField()
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.get_season_display()} {self.year}"

class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    reference = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    material = models.CharField(max_length=100)
    care_instructions = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference} - {self.name}"

class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    sku = models.CharField(max_length=50, unique=True)
    stock_quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=5)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    class Meta:
        unique_together = ['product', 'size', 'color']

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

class Discount(TimeStampedModel):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe')
    ]

    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField('Category', blank=True)
    collections = models.ManyToManyField(Collection, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ReturnPolicy(TimeStampedModel):
    RETURN_REASONS = [
        ('size', 'Mauvaise taille'),
        ('color', 'Mauvaise couleur'),
        ('defect', 'Défaut'),
        ('change_mind', 'Changement d\'avis'),
        ('other', 'Autre')
    ]

    sale = models.ForeignKey('pos.Sale', on_delete=models.PROTECT)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    reason = models.CharField(max_length=20, choices=RETURN_REASONS)
    description = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    processed_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    processed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Retour {self.id} - {self.sale.reference}"