"""Mixins de controle de acesso reutilizados em todas as views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


def is_admin(user):
    """True se o usuário é Administrador ou superusuário."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and profile.role == "admin")


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Permite acesso apenas a Administradores (ou superusuários)."""

    permission_denied_message = "Você não tem permissão para acessar o financeiro."

    def test_func(self):
        return is_admin(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, self.permission_denied_message)
        return redirect("dashboard")
