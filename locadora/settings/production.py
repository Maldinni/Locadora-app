"""Configurações de produção.

Pensado para VPS pequeno (ex.: Locaweb 512 MB):
- **SQLite com WAL** por padrão (não consome a RAM de um servidor Postgres).
  Para usar PostgreSQL, defina ``DB_ENGINE=postgres`` no ambiente.
- **WhiteNoise** serve os arquivos estáticos (sem nginx/Apache para estáticos).
- **Segurança HTTPS configurável** por ``ENABLE_HTTPS``: comece por IP (HTTP) e
  ligue o HTTPS depois, quando tiver domínio + certificado, sem mudar o código.
"""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, MIDDLEWARE, env, env_bool, env_list

DEBUG = False

# Em produção a SECRET_KEY DEVE vir do ambiente — nunca o default de dev.
if not os.environ.get("SECRET_KEY"):
    raise ImproperlyConfigured(
        "Defina a variável de ambiente SECRET_KEY em produção (gere um valor "
        "longo e aleatório)."
    )

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", [])

# --------------------------------------------------------------------------
# Arquivos estáticos (WhiteNoise)
# --------------------------------------------------------------------------
# Logo após o SecurityMiddleware, conforme recomendado.
MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# --------------------------------------------------------------------------
# Banco de dados
# --------------------------------------------------------------------------
# Padrão: SQLite (ideal para VPS pequeno). WAL + timeout deixam a escrita
# concorrente robusta para o volume de uma locadora pequena.
if env("DB_ENGINE", "sqlite").lower() == "postgres":
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
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {
                # Espera em vez de falhar na hora com "database is locked".
                "timeout": 10,
                # WAL: permite ler enquanto outra requisição escreve.
                "init_command": (
                    "PRAGMA journal_mode=WAL;"
                    "PRAGMA synchronous=NORMAL;"
                ),
            },
        }
    }

# --------------------------------------------------------------------------
# Segurança
# --------------------------------------------------------------------------
# Cabeçalhos seguros ficam sempre ligados.
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HTTPS: ligar apenas quando houver domínio + certificado (ENABLE_HTTPS=1).
# Com acesso por IP (HTTP), manter desligado para o site não ficar inacessível.
ENABLE_HTTPS = env_bool("ENABLE_HTTPS", False)
if ENABLE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Nginx encaminha o esquema original neste cabeçalho.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

_scheme = "https" if ENABLE_HTTPS else "http"
CSRF_TRUSTED_ORIGINS = [
    f"{_scheme}://{host}" for host in ALLOWED_HOSTS if host not in {"*", ""}
]
