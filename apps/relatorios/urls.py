from django.urls import path

from . import views

app_name = "relatorios"

urlpatterns = [
    path("financeiro/", views.RelatorioFinanceiroView.as_view(), name="financeiro"),
    path("financeiro/csv/", views.RelatorioCSVView.as_view(), name="financeiro_csv"),
]
