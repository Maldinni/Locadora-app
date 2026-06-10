"""Testes de clientes: validação de CPF, propriedades e formulário."""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.common.test_utils import CPF_VALIDO, make_cliente

from .forms import ClienteForm
from .validators import validate_cpf


class ValidateCpfTest(TestCase):
    def test_cpf_valido_retorna_digitos(self):
        self.assertEqual(validate_cpf("390.533.447-05"), CPF_VALIDO)

    def test_cpf_tamanho_errado(self):
        with self.assertRaises(ValidationError):
            validate_cpf("123")

    def test_cpf_sequencia_repetida(self):
        with self.assertRaises(ValidationError):
            validate_cpf("11111111111")

    def test_cpf_digito_verificador_invalido(self):
        with self.assertRaises(ValidationError):
            validate_cpf("39053344700")  # último dígito errado


class ClienteModelTest(TestCase):
    def test_cnh_vencida(self):
        vencido = make_cliente(
            cpf=CPF_VALIDO, validade_cnh=timezone.localdate() - timedelta(days=1)
        )
        self.assertTrue(vencido.cnh_vencida)

    def test_cnh_valida(self):
        ok = make_cliente(validade_cnh=timezone.localdate() + timedelta(days=10))
        self.assertFalse(ok.cnh_vencida)

    def test_cpf_formatado(self):
        cli = make_cliente()
        self.assertEqual(cli.cpf_formatado, "390.533.447-05")


class ClienteFormTest(TestCase):
    def _dados(self, **over):
        dados = dict(
            nome="Fulano de Tal",
            cpf="390.533.447-05",  # com máscara — deve ser normalizado
            cnh="98765432100",
            validade_cnh=(timezone.localdate() + timedelta(days=200)).isoformat(),
            telefone="11988887777",
            email="fulano@example.com",
            logradouro="Av. Brasil",
            numero="500",
            complemento="",
            bairro="Centro",
            cidade="Rio de Janeiro",
            uf="RJ",
            cep="20000-000",
        )
        dados.update(over)
        return dados

    def test_form_valido_normaliza_cpf(self):
        form = ClienteForm(data=self._dados())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["cpf"], CPF_VALIDO)

    def test_form_rejeita_cpf_invalido(self):
        form = ClienteForm(data=self._dados(cpf="123.456.789-00"))
        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)
