from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_interface, name='interface'),  # Page principale du POS
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('sales/', views.SaleListView.as_view(), name='sale-list'),
    path('sales/create/', views.SaleCreateView.as_view(), name='sale-create'),
]