from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserProfile

class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'core/user_list.html'
    context_object_name = 'users'
    permission_required = 'auth.view_user'

    def get_queryset(self):
        return User.objects.select_related('userprofile').all()

class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user-list')
    permission_required = 'auth.add_user'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Utilisateur créé avec succès')
        return response

class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user-list')
    permission_required = 'auth.change_user'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Utilisateur mis à jour avec succès')
        return response

class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'core/user_confirm_delete.html'
    success_url = reverse_lazy('core:user-list')
    permission_required = 'auth.delete_user'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Utilisateur supprimé avec succès')
        return response