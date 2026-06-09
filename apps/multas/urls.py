from django.urls import path

from . import views

app_name = "multas"

urlpatterns = [
    path("", views.MultaListView.as_view(), name="lista"),
    path("nova/", views.MultaCreateView.as_view(), name="nova"),
    path("<int:pk>/editar/", views.MultaUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.MultaDeleteView.as_view(), name="excluir"),
]
