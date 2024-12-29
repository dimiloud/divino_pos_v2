from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import io
from apps.inventory.models import Product, Category
from .models import Sale

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