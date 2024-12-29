from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_interface, name='interface'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('sales/', views.SaleListView.as_view(), name='sale-list'),
    path('sales/create/', views.SaleCreateView.as_view(), name='sale-create'),
]