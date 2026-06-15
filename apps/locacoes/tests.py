"""Testes de locações: cálculos, validações do formulário e regras de status."""
import tempfile
import zipfile
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.common.test_utils import (
    CPF_VALIDO_2,
    make_admin,
    make_cliente,
    make_locacao,
    make_veiculo,
)
from apps.configuracao.models import Configuracao
from apps.veiculos.models import Veiculo

from .forms import LocacaoForm
from .models import Locacao
from .services import render_contrato

_TMP_MEDIA = tempfile.mkdtemp()


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


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
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

    def test_criar_locacao_gera_contrato_e_libera(self):
        resp = self.client.post(reverse("locacoes:nova"), self._dados())
        self.assertEqual(resp.status_code, 302)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.ALUGADO)
        self.assertEqual(Locacao.objects.count(), 1)
        loc = Locacao.objects.get()
        # Contrato gerado → locação liberada (ativa) com arquivo e data.
        self.assertEqual(loc.status, Locacao.Status.ATIVO)
        self.assertTrue(loc.contrato)
        self.assertIsNotNone(loc.contrato_gerado_em)

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


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class ContratoTest(TestCase):
    def setUp(self):
        cfg = Configuracao.get_solo()
        cfg.nome_locador = "Auto Locadora LTDA"
        cfg.cpf_locador = "12.345.678/0001-90"
        cfg.endereco_locador = "Av. Central, 100, Teresina-PI"
        cfg.save()
        self.cliente = make_cliente(nome="Joana Teste")
        self.veiculo = make_veiculo()

    def _texto_contrato(self, locacao):
        arquivo = render_contrato(locacao)
        xml = zipfile.ZipFile(arquivo).read("word/document.xml").decode("utf-8")
        import re

        return re.sub("<[^>]+>", "", xml)

    def test_render_preenche_dados_do_locador_e_locatario(self):
        loc = make_locacao(
            cliente=self.cliente, veiculo=self.veiculo, valor_diaria=Decimal("100.00")
        )
        texto = self._texto_contrato(loc)
        self.assertIn("Auto Locadora LTDA", texto)         # locador (config)
        self.assertIn("Joana Teste", texto)                # locatário (cliente)
        self.assertIn(self.veiculo.placa, texto)           # veículo
        self.assertIn("700,00", texto)                     # diária 100 * 7 (semanal)
        # Dados sensíveis do modelo original não devem reaparecer.
        self.assertNotIn("Lucas de Paula", texto)

    def test_contrato_embute_logo(self):
        loc = make_locacao(cliente=self.cliente, veiculo=self.veiculo)
        arquivo = render_contrato(loc)
        nomes = zipfile.ZipFile(arquivo).namelist()
        self.assertTrue(any("word/media/" in n for n in nomes))

    def test_gerar_contrato_view_libera_locacao_pendente(self):
        self.client.force_login(make_admin())
        loc = make_locacao(
            cliente=self.cliente,
            veiculo=self.veiculo,
            status=Locacao.Status.PENDENTE,
        )
        resp = self.client.post(reverse("locacoes:gerar_contrato", args=[loc.pk]))
        self.assertEqual(resp.status_code, 302)
        loc.refresh_from_db()
        self.veiculo.refresh_from_db()
        self.assertEqual(loc.status, Locacao.Status.ATIVO)
        self.assertTrue(loc.contrato)
        self.assertEqual(self.veiculo.status, Veiculo.Status.ALUGADO)
