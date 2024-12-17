from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q
from .models import Product, ProductVariant, Collection, Size, Color, Discount
from .forms import ProductForm, ProductVariantForm, CollectionForm, DiscountForm

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        collection = self.request.GET.get('collection')

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(reference__icontains=q) |
                Q(description__icontains=q)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if collection:
            queryset = queryset.filter(collection_id=collection)

        return queryset

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Produit créé avec succès')
        return response

class ProductVariantCreateView(LoginRequiredMixin, CreateView):
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'inventory/product_variant_form.html'

    def get_success_url(self):
        return reverse_lazy('inventory:product-detail', kwargs={'pk': self.object.product.pk})

    def form_valid(self, form):
        product = Product.objects.get(pk=self.kwargs['product_pk'])
        form.instance.product = product

        if form.cleaned_data['create_multiple_sizes']:
            color = form.cleaned_data['color']
            base_sku = form.cleaned_data['sku']
            
            for size in Size.objects.all():
                # Créer une variante pour chaque taille
                variant = ProductVariant(
                    product=product,
                    size=size,
                    color=color,
                    sku=f"{base_sku}-{size.name}",
                    stock_quantity=form.cleaned_data['stock_quantity'],
                    minimum_stock=form.cleaned_data['minimum_stock']
                )
                variant.save()
            
            messages.success(self.request, 'Variantes créées avec succès')
            return redirect(self.get_success_url())

        return super().form_valid(form)

class CollectionListView(LoginRequiredMixin, ListView):
    model = Collection
    template_name = 'inventory/collection_list.html'
    context_object_name = 'collections'

class DiscountListView(LoginRequiredMixin, ListView):
    model = Discount
    template_name = 'inventory/discount_list.html'
    context_object_name = 'discounts'

    def get_queryset(self):
        return super().get_queryset().filter(active=True).order_by('-start_date')