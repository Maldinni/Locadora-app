from django.contrib import admin

from .models import Manutencao


@admin.register(Manutencao)
class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ("veiculo", "tipo_servico", "data", "custo", "km_momento", "proxima_revisao_km")
    list_filter = ("tipo_servico", "data")
    search_fields = ("veiculo__placa", "descricao")
    date_hierarchy = "data"
    autocomplete_fields = ("veiculo",)
