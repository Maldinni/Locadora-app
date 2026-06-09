from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Contas e acessos"

    def ready(self):
        # Conecta os signals (criação automática de Profile).
        from . import signals  # noqa: F401
