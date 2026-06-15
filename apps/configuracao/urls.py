from django.urls import path

from . import views

app_name = "configuracao"

urlpatterns = [
    path("", views.ConfiguracaoUpdateView.as_view(), name="editar"),
]
