from datetime import date

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel

# Placa no formato antigo (ABC1234) ou Mercosul (ABC1D23).
placa_validator = RegexValidator(
    regex=r"^[A-Z]{3}[0-9][0-9A-Z][0-9]{2}$",
    message="Placa inválida. Use o formato ABC1234 ou ABC1D23.",
)


class Veiculo(TimeStampedModel):
    class Status(models.TextChoices):
        DISPONIVEL = "disponivel", "Disponível"
        ALUGADO = "alugado", "Alugado"
        MANUTENCAO = "manutencao", "Em manutenção"
        VENDIDO = "vendido", "Vendido"

    class Categoria(models.TextChoices):
        BASICO = "basico", "Básico"
        INTERMEDIARIO = "intermediario", "Intermediário"
        SUV = "suv", "SUV"
        VAN = "van", "Van"

    # Identificação
    marca = models.CharField("marca", max_length=50)
    modelo = models.CharField("modelo", max_length=80)
    ano = models.PositiveIntegerField(
        "ano", validators=[MinValueValidator(1950)]
    )
    placa = models.CharField(
        "placa",
        max_length=7,
        unique=True,
        db_index=True,
        validators=[placa_validator],
    )
    quilometragem_atual = models.PositiveIntegerField("quilometragem atual", default=0)
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.DISPONIVEL,
        db_index=True,
    )
    categoria = models.CharField(
        "categoria",
        max_length=20,
        choices=Categoria.choices,
        db_index=True,
    )

    # Dados financeiros / documentação (opcionais)
    valor_compra = models.DecimalField(
        "valor de compra", max_digits=10, decimal_places=2, null=True, blank=True
    )
    valor_parcela = models.DecimalField(
        "valor da parcela", max_digits=10, decimal_places=2, null=True, blank=True
    )
    qtd_parcelas = models.PositiveIntegerField(
        "qtd. de parcelas", null=True, blank=True
    )
    parcelas_pagas = models.PositiveIntegerField(
        "parcelas já pagas", null=True, blank=True
    )
    tem_rastreador = models.BooleanField("possui rastreador do sistema", default=False)
    valor_rastreador = models.DecimalField(
        "valor mensal do rastreador", max_digits=10, decimal_places=2, null=True, blank=True
    )
    vencimento_ipva = models.DateField("vencimento do IPVA", null=True, blank=True)
    observacoes = models.TextField("observações", blank=True)

    # Manutenção em andamento
    manutencao_motivo = models.CharField("motivo da manutenção", max_length=200, blank=True)
    manutencao_retorno_previsto = models.DateField(
        "retorno previsto da manutenção", null=True, blank=True
    )

    class Meta:
        verbose_name = "veículo"
        verbose_name_plural = "veículos"
        ordering = ["marca", "modelo"]
        indexes = [
            models.Index(fields=["status", "categoria"]),
        ]

    def __str__(self):
        return f"{self.marca} {self.modelo} — {self.placa}"

    def get_absolute_url(self):
        return reverse("veiculos:detalhe", args=[self.pk])

    @property
    def descricao_curta(self):
        return f"{self.marca} {self.modelo} ({self.ano})"

    @property
    def disponivel(self):
        return self.status == self.Status.DISPONIVEL

    @property
    def parcelas_faltantes(self):
        """Parcelas restantes do financiamento, ou None se não houver dados."""
        if self.qtd_parcelas is None:
            return None
        return max(self.qtd_parcelas - (self.parcelas_pagas or 0), 0)

    @property
    def status_color(self):
        """Token de cor (Tailwind) para badges de status."""
        return {
            self.Status.DISPONIVEL: "green",
            self.Status.ALUGADO: "blue",
            self.Status.MANUTENCAO: "red",
            self.Status.VENDIDO: "gray",
        }.get(self.status, "gray")

    # ------------------------------------------------------------------
    # Helpers de vencimentos e revisões (usados no dashboard)
    # ------------------------------------------------------------------
    def proxima_revisao(self):
        """Retorna o registro de manutenção com revisão prevista mais próxima
        de ser atingida por quilometragem, ou None."""
        return (
            self.manutencoes.filter(proxima_revisao_km__isnull=False)
            .order_by("-data")
            .first()
        )

    def revisao_pendente(self):
        """True se a km atual já alcançou a próxima revisão prevista."""
        registro = self.proxima_revisao()
        if registro and registro.proxima_revisao_km:
            return self.quilometragem_atual >= registro.proxima_revisao_km
        return False

    def dias_para_vencimento(self, data_venc):
        if not data_venc:
            return None
        return (data_venc - date.today()).days
