from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime
from ..pos.services.return_analytics_service import ReturnAnalyticsService

class ReturnAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/return_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les filtres
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        category_id = self.request.GET.get('category')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Obtenir les statistiques
        analytics_service = ReturnAnalyticsService()
        stats = analytics_service.get_return_statistics(start_date, end_date)

        # Obtenir les tendances pour le graphique
        trends = analytics_service.get_return_trends()
        trend_data = {
            'labels': [t['month'].strftime('%b %Y') for t in trends],
            'returns': [t['total_returns'] for t in trends],
            'exchanges': [t['exchange_count'] for t in trends]
        }

        # Motifs de retour pour le graphique
        reasons = stats['return_reasons']
        reasons_data = {
            'labels': [r['reason'] for r in reasons],
            'values': [r['count'] for r in reasons]
        }

        # Produits les plus retournés
        product_returns = analytics_service.get_product_return_rates()
        if category_id:
            product_returns = product_returns.filter(product__category_id=category_id)
        top_returned_products = product_returns[:10]

        # Analyse des échanges de taille
        size_patterns = analytics_service.get_size_exchange_patterns()

        context.update({
            'stats': stats,
            'trend_data': trend_data,
            'reasons_data': reasons_data,
            'top_returned_products': top_returned_products,
            'size_exchange_patterns': size_patterns
        })

        return context