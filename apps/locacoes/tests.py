"""Testes de locações: cálculos, validações do formulário e regras de status."""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.common.test_utils import (
    CPF_VALIDO_2,
    make_admin,
    make_cliente,
    make_locacao,
    make_veiculo,
)
from apps.veiculos.models import Veiculo

from .forms import LocacaoForm
from .models import Locacao


class LocacaoCalculosTest(TestCase):
    def test_dias_e_valor_previsto(self):
        loc = make_locacao()  # 3 dias, diária 100
        self.assertEqual(loc.dias_previstos, 3)
        self.assertEqual(loc.valor_previsto, Decimal("300.00"))

    def test_sem_atraso(self):
        loc = make_locacao()
        loc.data_devolucao_real = loc.data_prevista_devolucao
        self.assertEqual(loc.dias_atraso, 0)
        self.assertEqual(loc.multa_sugerida, Decimal("0.00"))

    def test_atraso_gera_multa_sugerida(self):
        loc = make_locacao()
        loc.data_devolucao_real = loc.data_prevista_devolucao + timedelta(days=2)
        self.assertEqual(loc.dias_atraso, 2)
        # MULTA_DIARIA_ATRASO padrão = 150.00
        self.assertEqual(loc.multa_sugerida, Decimal("300.00"))

    def test_valor_total_usa_valor_final_quando_encerrado(self):
        loc = make_locacao(
            status=Locacao.Status.ENCERRADO, valor_final=Decimal("555.00")
        )
        self.assertEqual(loc.valor_total, Decimal("555.00"))

    def test_atrasada_property(self):
        loc = make_locacao(
            data_retirada=timezone.now() - timedelta(days=5),
            data_prevista_devolucao=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(loc.atrasada)


class LocacaoFormTest(TestCase):
    def setUp(self):
        self.cliente = make_cliente()
        self.veiculo = make_veiculo()

    def _dados(self, **over):
        agora = timezone.now()
        dados = dict(
            cliente=self.cliente.pk,
            veiculo=self.veiculo.pk,
            data_retirada=agora.strftime("%Y-%m-%dT%H:%M"),
            data_prevista_devolucao=(agora + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
            valor_diaria="120.00",
            km_saida=self.veiculo.quilometragem_atual,
            forma_pagamento=Locacao.FormaPagamento.PIX,
            observacoes="",
        )
        dados.update(over)
        return dados

    def test_form_valido(self):
        form = LocacaoForm(data=self._dados())
        self.assertTrue(form.is_valid(), form.errors)

    def test_bloqueia_cnh_vencida(self):
        self.cliente.validade_cnh = timezone.localdate() - timedelta(days=1)
        self.cliente.save()
        form = LocacaoForm(data=self._dados())
        self.assertFalse(form.is_valid())
        self.assertIn("cliente", form.errors)

    def test_bloqueia_veiculo_indisponivel(self):
        self.veiculo.status = Veiculo.Status.ALUGADO
        self.veiculo.save()
        form = LocacaoForm(data=self._dados())
        self.assertFalse(form.is_valid())
        # veículo nem aparece no queryset → erro de escolha inválida
        self.assertIn("veiculo", form.errors)

    def test_devolucao_anterior_a_retirada(self):
        agora = timezone.now()
        form = LocacaoForm(
            data=self._dados(
                data_prevista_devolucao=(agora - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("data_prevista_devolucao", form.errors)

    def test_km_saida_menor_que_atual(self):
        form = LocacaoForm(data=self._dados(km_saida=self.veiculo.quilometragem_atual - 1))
        self.assertFalse(form.is_valid())
        self.assertIn("km_saida", form.errors)


class LocacaoViewSideEffectsTest(TestCase):
    def setUp(self):
        self.client.force_login(make_admin())
        self.cliente = make_cliente()
        self.veiculo = make_veiculo()

    def _dados(self, **over):
        agora = timezone.now()
        dados = dict(
            cliente=self.cliente.pk,
            veiculo=self.veiculo.pk,
            data_retirada=agora.strftime("%Y-%m-%dT%H:%M"),
            data_prevista_devolucao=(agora + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
            valor_diaria="120.00",
            km_saida=self.veiculo.quilometragem_atual,
            forma_pagamento=Locacao.FormaPagamento.PIX,
            observacoes="",
        )
        dados.update(over)
        return dados

    def test_criar_locacao_marca_veiculo_alugado(self):
        resp = self.client.post(reverse("locacoes:nova"), self._dados())
        self.assertEqual(resp.status_code, 302)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.ALUGADO)
        self.assertEqual(Locacao.objects.count(), 1)

    def test_devolucao_libera_veiculo_e_atualiza_km(self):
        loc = make_locacao(cliente=self.cliente, veiculo=self.veiculo)
        self.veiculo.status = Veiculo.Status.ALUGADO
        self.veiculo.save()
        novo_km = self.veiculo.quilometragem_atual + 500
        resp = self.client.post(
            reverse("locacoes:devolucao", args=[loc.pk]),
            {
                "data_devolucao_real": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "km_retorno": novo_km,
                "valor_final": "360.00",
                "multa_atraso": "0.00",
            },
        )
        self.assertEqual(resp.status_code, 302)
        loc.refresh_from_db()
        self.veiculo.refresh_from_db()
        self.assertEqual(loc.status, Locacao.Status.ENCERRADO)
        self.assertEqual(self.veiculo.status, Veiculo.Status.DISPONIVEL)
        self.assertEqual(self.veiculo.quilometragem_atual, novo_km)

    def test_excluir_locacao_ativa_libera_veiculo(self):
        loc = make_locacao(cliente=self.cliente, veiculo=self.veiculo)
        self.veiculo.status = Veiculo.Status.ALUGADO
        self.veiculo.save()
        resp = self.client.post(reverse("locacoes:excluir", args=[loc.pk]))
        self.assertEqual(resp.status_code, 302)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.DISPONIVEL)
        self.assertFalse(Locacao.objects.filter(pk=loc.pk).exists())
