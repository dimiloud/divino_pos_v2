from django import forms
from .models import Product, ProductVariant, Collection, Size, Color, Discount

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'reference', 'description', 'category',
            'collection', 'base_price', 'tax_rate', 'material',
            'care_instructions', 'image', 'active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'care_instructions': forms.Textarea(attrs={'rows': 3}),
            'base_price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'tax_rate': forms.NumberInput(attrs={'min': '0', 'step': '0.1'})
        }

class ProductVariantForm(forms.ModelForm):
    create_multiple_sizes = forms.BooleanField(
        required=False,
        label='Créer pour toutes les tailles disponibles'
    )

    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'sku', 'stock_quantity', 'minimum_stock', 'barcode']
        widgets = {
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
            'minimum_stock': forms.NumberInput(attrs={'min': '0'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['create_multiple_sizes'].widget = forms.HiddenInput()

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'season', 'year', 'description', 'start_date', 'end_date', 'active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3})
        }

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['name', 'discount_type', 'value', 'start_date', 'end_date',
                 'products', 'categories', 'collections', 'active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'value': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'products': forms.SelectMultiple(attrs={'class': 'select2'}),
            'categories': forms.SelectMultiple(attrs={'class': 'select2'}),
            'collections': forms.SelectMultiple(attrs={'class': 'select2'})
        }