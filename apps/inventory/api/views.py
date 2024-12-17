from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Product, ProductVariant, StockMovement
from .serializers import ProductSerializer, ProductVariantSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        variant = get_object_or_404(ProductVariant, pk=request.data.get('variant_id'))
        adjustment = int(request.data.get('adjustment', 0))
        reason = request.data.get('reason', '')

        variant.stock_quantity += adjustment
        variant.save()

        StockMovement.objects.create(
            product=variant.product,
            variant=variant,
            quantity=abs(adjustment),
            movement_type='in' if adjustment > 0 else 'out',
            description=reason
        )

        return Response({'status': 'success'})
