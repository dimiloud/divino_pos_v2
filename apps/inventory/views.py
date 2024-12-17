from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import StockMovement, StockAlert
from apps.pos.models import Product

class StockMovementCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    fields = ['product', 'movement_type', 'quantity', 'notes']
    template_name = 'inventory/stock_movement_form.html'
    success_url = reverse_lazy('inventory:stock-movement-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Mouvement de stock enregistré avec succès')
        return response

class StockAlertListView(LoginRequiredMixin, ListView):
    model = StockAlert
    template_name = 'inventory/stock_alert_list.html'
    context_object_name = 'alerts'

    def get_queryset(self):
        return StockAlert.objects.filter(resolved=False)

class ProductStockUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['stock_quantity', 'minimum_stock']
    template_name = 'inventory/product_stock_form.html'
    success_url = reverse_lazy('inventory:product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        StockMovement.objects.create(
            product=self.object,
            movement_type='adjustment',
            quantity=form.cleaned_data['stock_quantity'],
            notes='Ajustement manuel du stock'
        )
        messages.success(self.request, 'Stock mis à jour avec succès')
        return response