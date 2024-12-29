from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Sale

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'pos/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by('-created_at')

class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    template_name = 'pos/sale_form.html'
    fields = ['payment_method', 'notes']
    success_url = reverse_lazy('pos:sale-list')

    def form_valid(self, form):
        form.instance.cashier = self.request.user
        form.instance.reference = Sale.generate_reference()
        response = super().form_valid(form)
        messages.success(self.request, 'Vente enregistrée avec succès')
        return response