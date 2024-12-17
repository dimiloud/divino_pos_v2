from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('sales/', views.SalesReportView.as_view(), name='sales-report'),
    path('inventory/', views.InventoryReportView.as_view(), name='inventory-report'),
    path('export/sales/', views.export_sales_report, name='export-sales'),
    path('export/inventory/', views.export_inventory_report, name='export-inventory'),
]