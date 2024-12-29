from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
import csv
import io
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

@login_required
def import_products(request):
    if request.method == 'POST' and request.FILES.get('file'):
        csv_file = request.FILES['file'].read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_file))
        
        success_count = 0
        error_count = 0
        
        for row in csv_reader:
            try:
                category, _ = Category.objects.get_or_create(
                    name=row.get('category', 'Autre')
                )
                
                Product.objects.create(
                    name=row['name'],
                    category=category,
                    price=float(row['price']),
                    stock_quantity=int(row.get('stock_quantity', 0)),
                    active=True
                )
                success_count += 1
            except Exception as e:
                error_count += 1
        
        if success_count:
            messages.success(request, f'{success_count} produits importés avec succès')
        if error_count:
            messages.error(request, f'{error_count} erreurs lors de l\'importation')
    
    return redirect('pos:product-list')