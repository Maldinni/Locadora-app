"""Disponibiliza o perfil do usuário em todos os templates."""
from .mixins import is_admin


def perfil(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"perfil_atual": None, "usuario_is_admin": False}
    return {
        "perfil_atual": getattr(user, "profile", None),
        "usuario_is_admin": is_admin(user),
    }
