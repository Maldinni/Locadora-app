"""Testes de contas: papel de acesso e proteção do dashboard."""
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from django.urls import reverse

from apps.common.test_utils import make_admin, make_operador

from .mixins import is_admin
from .models import Profile


class IsAdminTest(TestCase):
    def test_admin_por_papel(self):
        self.assertTrue(is_admin(make_admin()))

    def test_operador_nao_eh_admin(self):
        self.assertFalse(is_admin(make_operador()))

    def test_superusuario_eh_admin(self):
        su = User.objects.create_superuser("root@test.com", "root@test.com", "x")
        self.assertTrue(is_admin(su))

    def test_anonimo_nao_eh_admin(self):
        self.assertFalse(is_admin(AnonymousUser()))


class ProfileSignalTest(TestCase):
    def test_profile_criado_automaticamente(self):
        u = User.objects.create_user("novo@test.com", password="x")
        self.assertTrue(Profile.objects.filter(user=u).exists())
        self.assertEqual(u.profile.role, Profile.Role.OPERADOR)


class DashboardAcessoTest(TestCase):
    def test_dashboard_exige_login(self):
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/conta/login/", resp.url)

    def test_dashboard_sem_financeiro(self):
        # O dashboard não exibe mais informações financeiras (receita/gráficos),
        # nem para o admin.
        self.client.force_login(make_admin())
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Receita do mês atual")
        self.assertNotContains(resp, "Receita dos últimos 6 meses")

    def test_operador_acessa_dashboard(self):
        self.client.force_login(make_operador())
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)
