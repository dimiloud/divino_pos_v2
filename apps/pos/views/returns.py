from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from ..models import Return, Exchange, Sale
from ..forms import ReturnForm, ExchangeForm, ReturnProcessForm

class ReturnListView(LoginRequiredMixin, ListView):
    model = Return
    template_name = 'pos/returns/list.html'
    context_object_name = 'returns'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_counts'] = {
            status: Return.objects.filter(status=status).count()
            for status, _ in Return.RETURN_STATUS
        }
        return context

class ReturnCreateView(LoginRequiredMixin, CreateView):
    model = Return
    form_class = ReturnForm
    template_name = 'pos/returns/form.html'
    success_url = reverse_lazy('pos:return-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sale_id = self.kwargs.get('sale_id')
        if sale_id:
            kwargs['sale'] = get_object_or_404(Sale, id=sale_id)
        return kwargs

    def form_valid(self, form):
        return_obj = form.save(commit=False)
        return_obj.sale_id = self.kwargs.get('sale_id')
        return_obj.save()

        messages.success(self.request, 'Retour enregistré avec succès')
        return super().form_valid(form)

class ReturnDetailView(LoginRequiredMixin, DetailView):
    model = Return
    template_name = 'pos/returns/detail.html'
    context_object_name = 'return'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.status == 'approved':
            context['exchange_form'] = ExchangeForm(
                return_item=self.object
            )
        elif self.object.status == 'pending':
            context['process_form'] = ReturnProcessForm()
        return context

class ReturnProcessView(LoginRequiredMixin, UpdateView):
    model = Return
    form_class = ReturnProcessForm
    template_name = 'pos/returns/process.html'

    def form_valid(self, form):
        return_obj = self.object
        action = form.cleaned_data['action']

        if action == 'approve':
            return_obj.approve(self.request.user)
            messages.success(self.request, 'Retour approuvé avec succès')
        else:
            return_obj.reject(
                self.request.user,
                form.cleaned_data['reject_reason']
            )
            messages.warning(self.request, 'Retour refusé')

        return redirect('pos:return-detail', pk=return_obj.pk)

class ExchangeCreateView(LoginRequiredMixin, CreateView):
    model = Exchange
    form_class = ExchangeForm
    template_name = 'pos/returns/exchange_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return_id = self.kwargs.get('return_id')
        kwargs['return_item'] = get_object_or_404(Return, id=return_id)
        return kwargs

    def form_valid(self, form):
        exchange = form.save(commit=False)
        exchange.return_item_id = self.kwargs.get('return_id')
        
        # Calculer la différence de prix
        return_variant = exchange.return_item.product_variant
        new_variant = exchange.new_variant
        exchange.price_difference = (
            new_variant.product.base_price - return_variant.product.base_price
        )

        exchange.save()
        messages.success(self.request, 'Échange enregistré avec succès')
        return redirect('pos:return-detail', pk=exchange.return_item.pk)