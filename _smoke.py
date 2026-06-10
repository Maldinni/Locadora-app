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

r = c.post(
    f"/veiculos/{v}/status/",
    {
        "status": "manutencao",
        "manutencao_motivo": "Revisão de freios",
        "manutencao_retorno_previsto": "2030-01-15",
    },
)
veic = Veiculo.objects.get(pk=v)
ok_manut = (
    r.status_code == 200
    and veic.status == "manutencao"
    and veic.manutencao_motivo == "Revisão de freios"
    and str(veic.manutencao_retorno_previsto) == "2030-01-15"
)
print(f"HTMX -> manutencao (motivo + retorno): {'OK' if ok_manut else '!! FALHOU'}")
if not ok_manut:
    falhas += 1

# Volta para disponível: deve limpar motivo e data de retorno.
r = c.post(f"/veiculos/{v}/status/", {"status": "disponivel"})
veic.refresh_from_db()
ok_disp = (
    r.status_code == 200
    and veic.status == "disponivel"
    and veic.manutencao_motivo == ""
    and veic.manutencao_retorno_previsto is None
)
print(f"HTMX -> disponivel (limpa manutencao): {'OK' if ok_disp else '!! FALHOU'}")
if not ok_disp:
    falhas += 1

print("TOTAL FALHAS:", falhas)
