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
def pos_interface(request):
    products = Product.objects.filter(active=True)
    categories = Category.objects.filter(active=True)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'pos/pos_interface.html', context)