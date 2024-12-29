from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from apps.inventory.models import Product, Category

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'pos/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')

        if category:
            queryset = queryset.filter(category__id=category)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.filter(active=True)

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'pos/product_form.html'
    fields = ['name', 'category', 'price', 'stock_quantity', 'active']
    success_url = reverse_lazy('pos:product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Produit créé avec succès')
        return response