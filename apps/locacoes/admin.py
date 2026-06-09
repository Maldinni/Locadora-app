from django.contrib import admin

from .models import Locacao


@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "veiculo",
        "data_retirada",
        "data_prevista_devolucao",
        "status",
        "valor_diaria",
    )
    list_filter = ("status", "forma_pagamento")
    search_fields = ("cliente__nome", "cliente__cpf", "veiculo__placa")
    date_hierarchy = "data_retirada"
    autocomplete_fields = ("cliente", "veiculo")
