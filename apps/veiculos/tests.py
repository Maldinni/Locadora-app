"""Testes de veículos: propriedades e troca de status via HTMX."""
from django.test import TestCase
from django.urls import reverse

from apps.common.test_utils import make_admin, make_veiculo

from .models import Veiculo


class VeiculoModelTest(TestCase):
    def test_status_color(self):
        self.assertEqual(make_veiculo(status=Veiculo.Status.DISPONIVEL).status_color, "green")
        self.assertEqual(
            make_veiculo(placa="DEF4G56", status=Veiculo.Status.ALUGADO).status_color, "blue"
        )
        self.assertEqual(
            make_veiculo(placa="GHI7J89", status=Veiculo.Status.MANUTENCAO).status_color, "red"
        )

    def test_disponivel_property(self):
        self.assertTrue(make_veiculo().disponivel)
        self.assertFalse(make_veiculo(placa="DEF4G56", status=Veiculo.Status.ALUGADO).disponivel)


class VeiculoStatusViewTest(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)
        self.veiculo = make_veiculo()
        self.url = reverse("veiculos:status", args=[self.veiculo.pk])

    def test_exige_login(self):
        self.client.logout()
        resp = self.client.post(self.url, {"status": "manutencao", "manutencao_motivo": "x"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/conta/login/", resp.url)

    def test_para_manutencao_grava_motivo_e_retorno(self):
        resp = self.client.post(
            self.url,
            {
                "status": "manutencao",
                "manutencao_motivo": "Troca de pastilhas",
                "manutencao_retorno_previsto": "2030-05-10",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.MANUTENCAO)
        self.assertEqual(self.veiculo.manutencao_motivo, "Troca de pastilhas")
        self.assertEqual(str(self.veiculo.manutencao_retorno_previsto), "2030-05-10")

    def test_voltar_para_disponivel_limpa_manutencao(self):
        self.veiculo.status = Veiculo.Status.MANUTENCAO
        self.veiculo.manutencao_motivo = "algo"
        self.veiculo.save()
        resp = self.client.post(self.url, {"status": "disponivel"})
        self.assertEqual(resp.status_code, 200)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.DISPONIVEL)
        self.assertEqual(self.veiculo.manutencao_motivo, "")
        self.assertIsNone(self.veiculo.manutencao_retorno_previsto)

    def test_manutencao_sem_motivo_eh_rejeitada(self):
        resp = self.client.post(self.url, {"status": "manutencao", "manutencao_motivo": ""})
        self.assertEqual(resp.status_code, 200)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.DISPONIVEL)  # inalterado

    def test_veiculo_alugado_nao_muda_status(self):
        self.veiculo.status = Veiculo.Status.ALUGADO
        self.veiculo.save()
        resp = self.client.post(self.url, {"status": "disponivel"})
        self.assertEqual(resp.status_code, 200)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.ALUGADO)  # bloqueado

    def test_nao_permite_marcar_alugado_manualmente(self):
        resp = self.client.post(self.url, {"status": "alugado"})
        self.assertEqual(resp.status_code, 200)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.DISPONIVEL)  # inalterado

    def test_status_invalido(self):
        resp = self.client.post(self.url, {"status": "foobar"})
        self.assertEqual(resp.status_code, 200)
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.status, Veiculo.Status.DISPONIVEL)
