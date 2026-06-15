"""Rotas principais do projeto Locadora."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    path("conta/", include("apps.accounts.urls")),
    path("veiculos/", include("apps.veiculos.urls")),
    path("clientes/", include("apps.clientes.urls")),
    path("locacoes/", include("apps.locacoes.urls")),
    path("manutencao/", include("apps.manutencao.urls")),
    path("multas/", include("apps.multas.urls")),
    path("relatorios/", include("apps.relatorios.urls")),
    path("configuracao/", include("apps.configuracao.urls")),
]

# Em desenvolvimento, o Django serve os arquivos de mídia (contratos gerados).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
