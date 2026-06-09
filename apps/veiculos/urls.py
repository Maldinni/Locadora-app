from django.urls import path

from . import views

app_name = "veiculos"

urlpatterns = [
    path("", views.VeiculoListView.as_view(), name="lista"),
    path("novo/", views.VeiculoCreateView.as_view(), name="novo"),
    path("<int:pk>/", views.VeiculoDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", views.VeiculoUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.VeiculoDeleteView.as_view(), name="excluir"),
    path("<int:pk>/status/", views.VeiculoStatusView.as_view(), name="status"),
]
