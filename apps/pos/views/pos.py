from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from ..models import Product, Sale, SaleItem
from ..services.cart_service import CartService

@login_required
def pos_interface(request):
    # Récupérer les catégories actives avec leurs produits
    categories = Category.objects.filter(active=True).prefetch_related(
        'product_set__variants__size',
        'product_set__variants__color'
    )

    # Récupérer le panier actuel
    cart = CartService(request.session)
    
    context = {
        'categories': categories,
        'cart': cart.get_cart(),
        'cart_total': cart.get_total(),
        'cart_count': cart.get_count()
    }
    
    return render(request, 'pos/pos_interface.html', context)

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'pos/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(reference__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search)
            )

        return queryset.select_related('customer').order_by('-created_at')

class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'pos/sale_detail.html'
    context_object_name = 'sale'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter l'historique des retours
        context['returns'] = self.object.return_set.all().select_related(
            'product_variant__product',
            'product_variant__size',
            'product_variant__color'
        )
        return context