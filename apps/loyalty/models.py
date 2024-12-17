from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class LoyaltyCard(TimeStampedModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Bloquée')
    ]

    number = models.CharField(max_length=16, unique=True)
    customer = models.OneToOneField('Customer', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expiration_date = models.DateField()

    def add_points(self, amount):
        self.points += int(amount * settings.LOYALTY_POINTS_RATIO)
        self.save()

    def use_points(self, points):
        if self.points >= points:
            self.points -= points
            self.save()
            return True
        return False

class Customer(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()

class Promotion(TimeStampedModel):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
        ('points', 'Points')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    points_required = models.IntegerField(default=0)
    products = models.ManyToManyField('pos.Product', blank=True)
    categories = models.ManyToManyField('pos.Category', blank=True)

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_date <= now <= self.end_date

class PointsTransaction(TimeStampedModel):
    TRANSACTION_TYPES = [
        ('earn', 'Gagnés'),
        ('spend', 'Utilisés'),
        ('expired', 'Expirés'),
        ('adjusted', 'Ajustés')
    ]

    loyalty_card = models.ForeignKey(LoyaltyCard, on_delete=models.CASCADE)
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    sale = models.ForeignKey('pos.Sale', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)

class CustomerGroup(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    customers = models.ManyToManyField(Customer)
    promotions = models.ManyToManyField(Promotion, blank=True)
    min_points_required = models.IntegerField(default=0)

    def __str__(self):
        return self.name