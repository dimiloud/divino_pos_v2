from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib import messages
from apps.inventory.models import Product, Category
from .models import Sale

def pos_interface(request):
    products = Product.objects.filter(active=True)
    categories = Category.objects.filter(active=True)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'pos/pos_interface.html', context)

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

class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    template_name = 'pos/sale_form.html'
    fields = ['payment_method', 'notes']
    success_url = reverse_lazy('pos:sale-list')

    def form_valid(self, form):
        form.instance.cashier = self.request.user
        form.instance.reference = Sale.generate_reference()
        response = super().form_valid(form)
        messages.success(self.request, 'Vente enregistrée avec succès')
        return response

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'pos/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by('-created_at')