from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        raise PermissionDenied(_('Accès réservé au personnel'))

class CashierRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'cashier_profile')

    def handle_no_permission(self):
        raise PermissionDenied(_('Accès réservé aux caissiers'))

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff and self.request.user.has_perm('pos.manage_sales')

    def handle_no_permission(self):
        raise PermissionDenied(_('Accès réservé aux managers'))