from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf_formatado", "cnh", "validade_cnh", "telefone", "cidade", "uf")
    list_filter = ("uf",)
    search_fields = ("nome", "cpf", "cnh", "email")
    ordering = ("nome",)
