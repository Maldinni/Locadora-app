"""Testes do relatório financeiro: cálculo do serviço e acesso restrito."""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.common.test_utils import make_admin, make_cliente, make_locacao, make_operador, make_veiculo
from apps.locacoes.models import Locacao
from apps.manutencao.models import Manutencao

from .services import montar_relatorio


class MontarRelatorioTest(TestCase):
    def test_receita_custo_e_lucro(self):
        hoje = timezone.localdate()
        veiculo = make_veiculo(valor_parcela=Decimal("1000.00"))
        cliente = make_cliente()
        make_locacao(
            cliente=cliente,
            veiculo=veiculo,
            status=Locacao.Status.ENCERRADO,
            valor_final=Decimal("500.00"),
            data_devolucao_real=timezone.now(),
            km_retorno=veiculo.quilometragem_atual + 100,
        )
        Manutencao.objects.create(
            veiculo=veiculo,
            tipo_servico=Manutencao.Tipo.OLEO,
            data=hoje,
            custo=Decimal("200.00"),
            km_momento=veiculo.quilometragem_atual,
        )

        rel = montar_relatorio(hoje, hoje)
        self.assertEqual(rel.receita, Decimal("500.00"))
        self.assertEqual(rel.custo_manutencao, Decimal("200.00"))
        self.assertEqual(rel.meses_no_periodo, 1)
        self.assertEqual(rel.total_parcelas, Decimal("1000.00"))
        # lucro = 500 - 200 - 1000
        self.assertEqual(rel.lucro_estimado, Decimal("-700.00"))

    def test_fora_do_periodo_nao_conta(self):
        hoje = timezone.localdate()
        make_locacao(
            status=Locacao.Status.ENCERRADO,
            valor_final=Decimal("500.00"),
            data_retirada=timezone.now() - timedelta(days=40),
        )
        rel = montar_relatorio(hoje, hoje)
        self.assertEqual(rel.receita, Decimal("0.00"))


class RelatorioAcessoTest(TestCase):
    def test_operador_bloqueado(self):
        self.client.force_login(make_operador())
        resp = self.client.get(reverse("relatorios:financeiro"))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("dashboard"))

    def test_admin_acessa(self):
        self.client.force_login(make_admin())
        resp = self.client.get(reverse("relatorios:financeiro"))
        self.assertEqual(resp.status_code, 200)

    def test_csv_export(self):
        self.client.force_login(make_admin())
        resp = self.client.get(reverse("relatorios:financeiro_csv"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp["Content-Type"])
