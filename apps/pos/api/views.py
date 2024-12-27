from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Sale, SaleItem
from .serializers import SaleSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    
    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        today_sales = Sale.objects.filter(
            created_at__date=timezone.now().date()
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        return Response(today_sales)