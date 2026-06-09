from django.urls import path

from . import views

app_name = "locacoes"

urlpatterns = [
    path("", views.LocacaoListView.as_view(), name="lista"),
    path("nova/", views.LocacaoCreateView.as_view(), name="nova"),
    path("<int:pk>/", views.LocacaoDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", views.LocacaoUpdateView.as_view(), name="editar"),
    path("<int:pk>/devolucao/", views.LocacaoDevolucaoView.as_view(), name="devolucao"),
    path("<int:pk>/excluir/", views.LocacaoDeleteView.as_view(), name="excluir"),
]
