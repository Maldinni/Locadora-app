import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "locadora.settings.development")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.veiculos.models import Veiculo
from apps.clientes.models import Cliente
from apps.locacoes.models import Locacao

c = Client()
admin = User.objects.get(username="admin@locadora.com")
c.force_login(admin)

v = Veiculo.objects.first().pk
cli = Cliente.objects.first().pk
loc = Locacao.objects.first().pk
loc_ativa = Locacao.objects.filter(status="ativo").first().pk

urls = [
    "/", "/veiculos/", f"/veiculos/{v}/", f"/veiculos/{v}/editar/", "/veiculos/novo/",
    "/clientes/", f"/clientes/{cli}/", "/clientes/novo/",
    "/locacoes/", f"/locacoes/{loc}/", "/locacoes/nova/", f"/locacoes/{loc_ativa}/devolucao/",
    "/manutencao/", "/manutencao/nova/",
    "/multas/", "/multas/nova/",
    "/relatorios/financeiro/", "/relatorios/financeiro/csv/",
    "/conta/senha/",
]
falhas = 0
for u in urls:
    r = c.get(u)
    if r.status_code != 200:
        falhas += 1
    print(f"{'OK ' if r.status_code == 200 else '!! '}{r.status_code}  {u}")

op = User.objects.get(username="operador@locadora.com")
c2 = Client()
c2.force_login(op)
r = c2.get("/relatorios/financeiro/")
print(f"operador -> relatorios: {r.status_code} (esperado 302)")

r = c.post(f"/veiculos/{v}/status/", {"status": "manutencao", "manutencao_motivo": "teste"})
print(f"HTMX status change: {r.status_code} (esperado 200)")

print("TOTAL FALHAS:", falhas)
