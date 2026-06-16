"""Configuração do Gunicorn para produção em VPS pequeno (~512 MB).

Uso:
    gunicorn locadora.wsgi:application -c gunicorn.conf.py
"""

# Porta local — o Nginx faz o proxy reverso para cá.
bind = "127.0.0.1:8000"

# Número de workers FIXO em 2: cabe com folga em 512 MB de RAM.
# (A fórmula 2*CPU+1 não se aplica aqui porque o gargalo é memória, não CPU.)
workers = 2
worker_class = "sync"

# Tempo máximo de uma requisição (geração de contrato .docx pode demorar).
timeout = 60
graceful_timeout = 30
keepalive = 5

# Recicla cada worker a cada N requisições para evitar acúmulo de memória.
max_requests = 500
max_requests_jitter = 50

# Logs vão para o journald (systemd) via stdout/stderr.
accesslog = "-"
errorlog = "-"
loglevel = "info"
