"""Configurações de produção: PostgreSQL + DEBUG desligado + segurança."""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, env, env_list

DEBUG = False

# Em produção a SECRET_KEY DEVE vir do ambiente — nunca o default de dev.
if not os.environ.get("SECRET_KEY"):
    raise ImproperlyConfigured(
        "Defina a variável de ambiente SECRET_KEY em produção (gere um valor "
        "longo e aleatório)."
    )

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", [])

# WhiteNoise serve os arquivos estáticos sem precisar de nginx/Apache.
# Logo após o SecurityMiddleware, conforme recomendado.
MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "locadora"),
        "USER": env("POSTGRES_USER", "locadora"),
        "PASSWORD": env("POSTGRES_PASSWORD", ""),
        "HOST": env("POSTGRES_HOST", "127.0.0.1"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

# --------------------------------------------------------------------------
# Segurança (HTTPS / cookies / cabeçalhos)
# --------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in {"*", ""}
]
