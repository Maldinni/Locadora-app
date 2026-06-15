from django.contrib import admin

from .models import Configuracao


@admin.register(Configuracao)
class ConfiguracaoAdmin(admin.ModelAdmin):
    list_display = ("nome_locador", "cpf_locador", "updated_at")

    def has_add_permission(self, request):
        # Singleton: impede criar mais de uma linha pela admin.
        return not Configuracao.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
