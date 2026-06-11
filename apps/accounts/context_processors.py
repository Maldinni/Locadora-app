"""Disponibiliza o perfil do usuário e estatísticas da navegação."""
from django.db.models import Count

from .mixins import is_admin


def perfil(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"perfil_atual": None, "usuario_is_admin": False}
    return {
        "perfil_atual": getattr(user, "profile", None),
        "usuario_is_admin": is_admin(user),
    }


def nav_stats(request):
    """Contagens leves usadas nos badges e no indicador da sidebar."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {}

    # Import local para evitar ciclos no carregamento do módulo.
    from apps.multas.models import Multa
    from apps.veiculos.models import Veiculo

    contagens = {
        linha["status"]: linha["n"]
        for linha in Veiculo.objects.values("status").annotate(n=Count("id"))
    }
    return {
        "nav_veiculos_total": sum(contagens.values()),
        "nav_veiculos_alugados": contagens.get(Veiculo.Status.ALUGADO, 0),
        "nav_manutencao_count": contagens.get(Veiculo.Status.MANUTENCAO, 0),
        "nav_multas_pendentes": Multa.objects.filter(status=Multa.Status.PENDENTE).count(),
    }
