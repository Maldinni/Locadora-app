#!/usr/bin/env python
"""Utilitário de linha de comando do Django para tarefas administrativas."""
import os
import sys

from dotenv import load_dotenv


def main():
    # Carrega variáveis do arquivo .env (se existir) antes de tudo.
    load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "locadora.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Ele está instalado e "
            "disponível na sua variável de ambiente PYTHONPATH? Você "
            "esqueceu de ativar a virtualenv?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
