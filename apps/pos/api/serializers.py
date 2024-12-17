from rest_framework import serializers
from apps.pos.models import Product, Category, Sale, SaleItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'active']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    margin = serializers.DecimalField(source='get_margin', max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'description',
            'price', 'cost', 'margin', 'barcode', 'stock_quantity',
            'minimum_stock', 'image', 'active'
        ]

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'quantity',
            'unit_price', 'total_price', 'discount'
        ]

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    cashier_name = serializers.CharField(source='cashier.get_full_name', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'reference', 'cashier', 'cashier_name', 'total_amount',
            'payment_method', 'payment_status', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['reference', 'cashier']