"""Popula o banco com dados de demonstração realistas (pt_BR)."""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from apps.accounts.models import Profile
from apps.clientes.models import Cliente
from apps.locacoes.models import Locacao
from apps.manutencao.models import Manutencao
from apps.multas.models import Multa
from apps.veiculos.models import Veiculo

fake = Faker("pt_BR")

MODELOS = [
    ("Fiat", "Mobi", "basico"),
    ("Volkswagen", "Gol", "basico"),
    ("Chevrolet", "Onix", "intermediario"),
    ("Hyundai", "HB20", "intermediario"),
    ("Jeep", "Renegade", "suv"),
    ("Honda", "HR-V", "suv"),
    ("Renault", "Kwid", "basico"),
    ("Toyota", "Corolla", "intermediario"),
    ("Fiat", "Toro", "suv"),
    ("Renault", "Master", "van"),
]
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def placa_aleatoria():
    l = "".join(random.choices(LETRAS, k=3))
    return f"{l}{random.randint(0,9)}{random.choice(LETRAS+'0123456789')}{random.randint(0,9)}{random.randint(0,9)}"


class Command(BaseCommand):
    help = "Cria usuários, veículos, clientes, locações, manutenções e multas de demonstração."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        Faker.seed(42)

        self.stdout.write("Limpando dados anteriores...")
        Multa.objects.all().delete()
        Manutencao.objects.all().delete()
        Locacao.objects.all().delete()
        Cliente.objects.all().delete()
        Veiculo.objects.all().delete()

        self._criar_usuarios()
        veiculos = self._criar_veiculos()
        clientes = self._criar_clientes()
        self._criar_locacoes(clientes, veiculos)
        self._criar_manutencoes(veiculos)
        self._criar_multas(veiculos)

        self.stdout.write(self.style.SUCCESS("\nDados de demonstração criados com sucesso!"))
        self.stdout.write("  Admin:    admin@locadora.com / admin123")
        self.stdout.write("  Operador: operador@locadora.com / op123")

    # ------------------------------------------------------------------
    def _criar_usuarios(self):
        self.stdout.write("Criando usuários...")
        admin, criado = User.objects.get_or_create(
            username="admin@locadora.com",
            defaults={"email": "admin@locadora.com", "first_name": "Administrador",
                      "is_staff": True, "is_superuser": True},
        )
        admin.set_password("admin123")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        Profile.objects.update_or_create(user=admin, defaults={"role": Profile.Role.ADMIN})

        op, criado = User.objects.get_or_create(
            username="operador@locadora.com",
            defaults={"email": "operador@locadora.com", "first_name": "Operador"},
        )
        op.set_password("op123")
        op.save()
        Profile.objects.update_or_create(user=op, defaults={"role": Profile.Role.OPERADOR})

    def _criar_veiculos(self):
        self.stdout.write("Criando veículos...")
        veiculos = []
        placas = set()
        for i in range(8):
            marca, modelo, categoria = MODELOS[i]
            placa = placa_aleatoria()
            while placa in placas:
                placa = placa_aleatoria()
            placas.add(placa)
            v = Veiculo.objects.create(
                marca=marca,
                modelo=modelo,
                ano=random.randint(2018, 2024),
                placa=placa,
                quilometragem_atual=random.randint(15000, 90000),
                status=Veiculo.Status.DISPONIVEL,
                categoria=categoria,
                valor_compra=Decimal(random.randint(60, 160) * 1000),
                valor_parcela=Decimal(random.randint(900, 2200)),
                qtd_parcelas=48,
                vencimento_ipva=timezone.localdate() + timedelta(days=random.randint(-10, 60)),
                vencimento_seguro=timezone.localdate() + timedelta(days=random.randint(5, 120)),
            )
            veiculos.append(v)

        # Um veículo em manutenção.
        veiculos[0].status = Veiculo.Status.MANUTENCAO
        veiculos[0].manutencao_motivo = "Revisão de freios e suspensão"
        veiculos[0].manutencao_retorno_previsto = timezone.localdate() + timedelta(days=4)
        veiculos[0].save()
        return veiculos

    def _criar_clientes(self):
        self.stdout.write("Criando clientes...")
        clientes = []
        cpfs = set()
        for i in range(15):
            cpf = fake.cpf().replace(".", "").replace("-", "")
            while cpf in cpfs:
                cpf = fake.cpf().replace(".", "").replace("-", "")
            cpfs.add(cpf)
            # O primeiro cliente tem CNH vencida (demonstra o bloqueio).
            if i == 0:
                validade = timezone.localdate() - timedelta(days=30)
            else:
                validade = timezone.localdate() + timedelta(days=random.randint(120, 1500))
            clientes.append(
                Cliente.objects.create(
                    nome=fake.name(),
                    cpf=cpf,
                    cnh=str(fake.random_number(digits=11, fix_len=True)),
                    validade_cnh=validade,
                    telefone=fake.phone_number()[:20],
                    email=fake.free_email(),
                    logradouro=fake.street_name(),
                    numero=str(fake.building_number()),
                    bairro=fake.bairro(),
                    cidade=fake.city(),
                    uf=fake.estado_sigla(),
                    cep=fake.postcode(),
                )
            )
        return clientes

    def _criar_locacoes(self, clientes, veiculos):
        self.stdout.write("Criando locações...")
        agora = timezone.now()
        disponiveis = [v for v in veiculos if v.status == Veiculo.Status.DISPONIVEL]
        clientes_ok = [c for c in clientes if not c.cnh_vencida]

        # 3 locações ativas (veículo passa a alugado).
        for v in random.sample(disponiveis, 3):
            retirada = agora - timedelta(days=random.randint(1, 6), hours=random.randint(0, 12))
            prevista = retirada + timedelta(days=random.randint(3, 10))
            Locacao.objects.create(
                cliente=random.choice(clientes_ok),
                veiculo=v,
                data_retirada=retirada,
                data_prevista_devolucao=prevista,
                valor_diaria=Decimal(random.randint(90, 260)),
                km_saida=v.quilometragem_atual,
                forma_pagamento=random.choice(Locacao.FormaPagamento.values),
                status=Locacao.Status.ATIVO,
            )
            v.status = Veiculo.Status.ALUGADO
            v.save(update_fields=["status"])

        # 17 locações encerradas no último trimestre.
        for _ in range(17):
            retirada = agora - timedelta(days=random.randint(7, 90), hours=random.randint(0, 12))
            dias = random.randint(2, 12)
            prevista = retirada + timedelta(days=dias)
            # Atraso ocasional.
            atraso = random.choice([0, 0, 0, 1, 2])
            real = prevista + timedelta(days=atraso)
            diaria = Decimal(random.randint(90, 260))
            km_saida = random.randint(15000, 90000)
            Locacao.objects.create(
                cliente=random.choice(clientes_ok),
                veiculo=random.choice(veiculos),
                data_retirada=retirada,
                data_prevista_devolucao=prevista,
                valor_diaria=diaria,
                km_saida=km_saida,
                forma_pagamento=random.choice(Locacao.FormaPagamento.values),
                status=Locacao.Status.ENCERRADO,
                data_devolucao_real=real,
                km_retorno=km_saida + random.randint(150, 2500),
                multa_atraso=Decimal(atraso) * Decimal("150.00"),
                valor_final=diaria * dias + Decimal(atraso) * Decimal("150.00"),
            )

    def _criar_manutencoes(self, veiculos):
        self.stdout.write("Criando manutenções...")
        for i in range(10):
            v = random.choice(veiculos)
            data = timezone.localdate() - timedelta(days=random.randint(10, 200))
            km = max(1000, v.quilometragem_atual - random.randint(1000, 8000))
            # Algumas com próxima revisão já vencida (alerta no dashboard).
            if i < 3:
                proxima_km = v.quilometragem_atual - random.randint(100, 1500)
            else:
                proxima_km = v.quilometragem_atual + random.randint(3000, 12000)
            Manutencao.objects.create(
                veiculo=v,
                tipo_servico=random.choice(Manutencao.Tipo.values),
                descricao=fake.sentence(nb_words=6),
                data=data,
                custo=Decimal(random.randint(150, 1800)),
                km_momento=km,
                proxima_revisao_km=proxima_km,
                proxima_revisao_data=data + timedelta(days=180),
            )

    def _criar_multas(self, veiculos):
        self.stdout.write("Criando multas...")
        contratos = list(Locacao.objects.all())
        for _ in range(3):
            contrato = random.choice(contratos) if contratos else None
            veiculo = contrato.veiculo if contrato else random.choice(veiculos)
            Multa.objects.create(
                veiculo=veiculo,
                contrato=contrato,
                data_infracao=timezone.localdate() - timedelta(days=random.randint(5, 60)),
                valor=Decimal(random.choice([88, 130, 195, 293])),
                descricao=random.choice([
                    "Excesso de velocidade",
                    "Estacionamento proibido",
                    "Avanço de sinal vermelho",
                ]),
                status=Multa.Status.PENDENTE,
            )
