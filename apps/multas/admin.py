from django.contrib import admin

from .models import Multa


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ("veiculo", "data_infracao", "valor", "status", "contrato")
    list_filter = ("status", "data_infracao")
    search_fields = ("veiculo__placa", "descricao")
    autocomplete_fields = ("veiculo", "contrato")
