"""Configurações de desenvolvimento: SQLite + DEBUG ligado."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Em desenvolvimento, e-mails vão para o console.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
