from django import forms
from .models import Return, Exchange, ReturnReason

class ReturnForm(forms.ModelForm):
    confirm_receipt = forms.BooleanField(
        required=True,
        label='J\'ai vérifié le ticket de caisse'
    )
    confirm_condition = forms.BooleanField(
        required=True,
        label='L\'article est en bon état et avec étiquettes'
    )

    class Meta:
        model = Return
        fields = ['product_variant', 'quantity', 'reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, sale=None, **kwargs):
        super().__init__(*args, **kwargs)
        if sale:
            # Filtrer les variants disponibles pour ce ticket
            self.fields['product_variant'].queryset = sale.get_returnable_variants()

class ExchangeForm(forms.ModelForm):
    class Meta:
        model = Exchange
        fields = ['new_variant']

    def __init__(self, *args, return_item=None, **kwargs):
        super().__init__(*args, **kwargs)
        if return_item:
            # Filtrer les variants disponibles pour l'échange (même produit, taille différente)
            self.fields['new_variant'].queryset = (
                return_item.product_variant.product.variants
                .exclude(pk=return_item.product_variant.pk)
                .filter(stock_quantity__gt=0)
            )

class ReturnProcessForm(forms.Form):
    action = forms.ChoiceField(
        choices=[('approve', 'Approuver'), ('reject', 'Rejeter')],
        widget=forms.RadioSelect
    )
    reject_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('action') == 'reject' and not cleaned_data.get('reject_reason'):
            raise forms.ValidationError(
                'Une raison est requise pour le rejet du retour'
            )
        return cleaned_data