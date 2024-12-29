from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils.translation import gettext as _

from apps.core.mixins import CashierRequiredMixin
from apps.inventory.models import Product, Category
from ..models import Sale, SaleItem

@login_required
def pos_interface(request):
    products = Product.objects.filter(active=True)\
        .select_related('category')\
        .order_by('category__name', 'name')
    
    categories = Category.objects.filter(active=True)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'pos/pos_interface.html', context)

@login_required
@transaction.atomic
def process_sale(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = request.POST
        products_data = request.POST.getlist('products[]')
        
        # Création de la vente
        sale = Sale.objects.create(
            cashier=request.user,
            payment_method=data['payment_method'],
            notes=data.get('notes', '')
        )
        
        # Ajout des produits
        for product_data in products_data:
            product_id = product_data['id']
            quantity = int(product_data['quantity'])
            
            product = Product.objects.select_for_update().get(id=product_id)
            
            if product.stock_quantity < quantity:
                raise ValueError(f'Stock insuffisant pour {product.name}')
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )
            
            # Mise à jour du stock
            product.stock_quantity -= quantity
            product.save()
        
        sale.calculate_totals()
        sale.save()
        
        messages.success(request, _('Vente enregistrée avec succès'))
        return JsonResponse({
            'success': True,
            'sale_id': sale.id,
            'total': str(sale.total)
        })
        
    except Product.DoesNotExist:
        return JsonResponse({'error': _('Produit non trouvé')}, status=404)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': _('Erreur lors de la vente')}, status=500)

@login_required
def get_product_info(request, product_id):
    try:
        product = Product.objects.get(id=product_id, active=True)
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock_quantity
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': _('Produit non trouvé')}, status=404)