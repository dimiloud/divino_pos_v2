from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.inventory.models import Product, Category

@login_required
def pos_interface(request):
    products = Product.objects.filter(active=True)
    categories = Category.objects.filter(active=True)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'pos/pos_interface.html', context)