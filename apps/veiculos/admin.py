from django.contrib import admin

from .models import Veiculo


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "ano", "categoria", "status", "quilometragem_atual")
    list_filter = ("status", "categoria", "marca")
    search_fields = ("placa", "modelo", "marca")
    ordering = ("marca", "modelo")
