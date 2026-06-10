"""Factories e CPFs válidos reutilizados pelos testes dos apps."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.utils import timezone

from apps.accounts.models import Profile
from apps.clientes.models import Cliente
from apps.locacoes.models import Locacao
from apps.veiculos.models import Veiculo

# CPFs com dígitos verificadores corretos (para testes que precisam passar).
CPF_VALIDO = "39053344705"
CPF_VALIDO_2 = "11144477735"


def make_admin(username="admin@test.com", password="senha-test-123"):
    """Administrador via papel (não-superusuário) — exercita is_admin pelo role."""
    user = User.objects.create_user(username=username, email=username, password=password)
    # O signal cria um Profile OPERADOR; promovemos a ADMIN.
    profile = user.profile
    profile.role = Profile.Role.ADMIN
    profile.save()
    return user


def make_operador(username="op@test.com", password="senha-test-123"):
    return User.objects.create_user(username=username, email=username, password=password)


def make_veiculo(**kwargs):
    defaults = dict(
        marca="Fiat",
        modelo="Mobi",
        ano=2022,
        placa="ABC1D23",
        quilometragem_atual=10000,
        status=Veiculo.Status.DISPONIVEL,
        categoria=Veiculo.Categoria.BASICO,
    )
    defaults.update(kwargs)
    return Veiculo.objects.create(**defaults)


def make_cliente(**kwargs):
    defaults = dict(
        nome="Cliente Teste",
        cpf=CPF_VALIDO,
        cnh="12345678900",
        validade_cnh=timezone.localdate() + timedelta(days=365),
        telefone="11999990000",
        email="cliente@test.com",
        logradouro="Rua A",
        numero="100",
        bairro="Centro",
        cidade="São Paulo",
        uf="SP",
        cep="01000-000",
    )
    defaults.update(kwargs)
    return Cliente.objects.create(**defaults)


def make_locacao(cliente=None, veiculo=None, **kwargs):
    cliente = cliente or make_cliente()
    veiculo = veiculo or make_veiculo()
    agora = timezone.now()
    defaults = dict(
        cliente=cliente,
        veiculo=veiculo,
        data_retirada=agora,
        data_prevista_devolucao=agora + timedelta(days=3),
        valor_diaria=Decimal("100.00"),
        km_saida=veiculo.quilometragem_atual,
        forma_pagamento=Locacao.FormaPagamento.PIX,
        status=Locacao.Status.ATIVO,
    )
    defaults.update(kwargs)
    return Locacao.objects.create(**defaults)
