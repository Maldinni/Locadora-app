"""Configuração WSGI para o projeto Locadora."""
import os

from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application

# Carrega o .env antes de tudo, para o Gunicorn enxergar SECRET_KEY,
# DJANGO_SETTINGS_MODULE e demais variáveis (igual ao manage.py).
load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "locadora.settings.development")

application = get_wsgi_application()
