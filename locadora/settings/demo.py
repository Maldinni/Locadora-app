"""Settings de demonstração (ex.: PythonAnywhere free).

DEBUG desligado, banco SQLite (suficiente para a demo) e WhiteNoise servindo
os arquivos estáticos — assim não é preciso configurar mapeamento de estáticos
no painel do host. Use definindo:

    DJANGO_SETTINGS_MODULE=locadora.settings.demo
"""
from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, env, env_list

DEBUG = False

# Aceita qualquer subdomínio *.pythonanywhere.com (e local, para testes).
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS", [".pythonanywhere.com", "localhost", "127.0.0.1"]
)

# Usa a SECRET_KEY do ambiente se houver; senão herda a do base.
# Para a demo é aceitável, mas o ideal é definir uma SECRET_KEY própria.
SECRET_KEY = env("SECRET_KEY", SECRET_KEY)  # noqa: F405

# Banco: SQLite (herdado do base) — não precisa de PostgreSQL para a demo.

# WhiteNoise serve os estáticos diretamente pelo app (sem nginx/mapeamento).
MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Versão sem manifesto: mais tolerante (não quebra se faltar um arquivo).
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# O domínio padrão do PythonAnywhere é servido por HTTPS — libera o POST/CSRF.
CSRF_TRUSTED_ORIGINS = ["https://*.pythonanywhere.com"]
