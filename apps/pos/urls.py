from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    # Interface principale POS
    path('', views.pos_interface, name='pos-interface'),
    path('sales/', views.SaleListView.as_view(), name='sale-list'),
    path('sales/<int:pk>/', views.SaleDetailView.as_view(), name='sale-detail'),
    path('sales/create/', views.SaleCreateView.as_view(), name='sale-create'),
    
    # Gestion des retours
    path('returns/', views.returns.ReturnListView.as_view(), name='return-list'),
    path('returns/create/<int:sale_id>/', views.returns.ReturnCreateView.as_view(), name='return-create'),
    path('returns/<int:pk>/', views.returns.ReturnDetailView.as_view(), name='return-detail'),
    path('returns/<int:pk>/process/', views.returns.ReturnProcessView.as_view(), name='return-process'),
    
    # Gestion des échanges
    path('returns/<int:return_id>/exchange/', views.returns.ExchangeCreateView.as_view(), name='exchange-create'),
    
    # Gestion des produits
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    # API endpoints pour l'interface POS
    path('api/cart/add/', views.api.add_to_cart, name='api-cart-add'),
    path('api/cart/remove/', views.api.remove_from_cart, name='api-cart-remove'),
    path('api/cart/update/', views.api.update_cart_item, name='api-cart-update'),
    path('api/cart/clear/', views.api.clear_cart, name='api-cart-clear'),
    path('api/products/search/', views.api.search_products, name='api-product-search'),
]