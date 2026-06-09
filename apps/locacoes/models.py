import math
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel


def _multa_diaria_padrao():
    return Decimal(str(settings.MULTA_DIARIA_ATRASO))


def _dias_entre(inicio, fim):
    """Quantidade de diárias (arredonda pra cima, mínimo 1)."""
    if not inicio or not fim:
        return 0
    delta = fim - inicio
    dias = math.ceil(delta.total_seconds() / 86400)
    return max(1, dias)


class Locacao(TimeStampedModel):
    class Status(models.TextChoices):
        ATIVO = "ativo", "Ativo"
        ENCERRADO = "encerrado", "Encerrado"

    class FormaPagamento(models.TextChoices):
        PIX = "pix", "PIX"
        DINHEIRO = "dinheiro", "Dinheiro"
        CARTAO = "cartao", "Cartão"

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="locacoes",
        verbose_name="cliente",
    )
    veiculo = models.ForeignKey(
        "veiculos.Veiculo",
        on_delete=models.PROTECT,
        related_name="locacoes",
        verbose_name="veículo",
    )

    data_retirada = models.DateTimeField("data/hora de retirada")
    data_prevista_devolucao = models.DateTimeField("data/hora prevista de devolução")
    valor_diaria = models.DecimalField("valor da diária", max_digits=10, decimal_places=2)
    km_saida = models.PositiveIntegerField("quilometragem de saída")
    forma_pagamento = models.CharField(
        "forma de pagamento", max_length=20, choices=FormaPagamento.choices
    )
    observacoes = models.TextField("observações", blank=True)

    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.ATIVO, db_index=True
    )

    # Preenchidos na devolução
    data_devolucao_real = models.DateTimeField("devolução real", null=True, blank=True)
    km_retorno = models.PositiveIntegerField("quilometragem de retorno", null=True, blank=True)
    valor_final = models.DecimalField(
        "valor final cobrado", max_digits=10, decimal_places=2, null=True, blank=True
    )
    multa_atraso = models.DecimalField(
        "multa por atraso", max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        verbose_name = "locação"
        verbose_name_plural = "locações"
        ordering = ["-data_retirada"]
        indexes = [models.Index(fields=["status", "data_retirada"])]

    def __str__(self):
        return f"Locação #{self.pk} — {self.cliente} / {self.veiculo.placa}"

    def get_absolute_url(self):
        return reverse("locacoes:detalhe", args=[self.pk])

    # ------------------------------------------------------------------
    # Cálculos
    # ------------------------------------------------------------------
    @property
    def dias_previstos(self):
        return _dias_entre(self.data_retirada, self.data_prevista_devolucao)

    @property
    def valor_previsto(self):
        return (self.valor_diaria or Decimal("0")) * self.dias_previstos

    @property
    def dias_atraso(self):
        if not self.data_devolucao_real:
            return 0
        if self.data_devolucao_real <= self.data_prevista_devolucao:
            return 0
        delta = self.data_devolucao_real - self.data_prevista_devolucao
        return max(0, math.ceil(delta.total_seconds() / 86400))

    @property
    def multa_sugerida(self):
        return self.dias_atraso * _multa_diaria_padrao()

    @property
    def valor_total(self):
        """Valor a cobrar: usa o valor final quando encerrado; senão estimado."""
        if self.status == self.Status.ENCERRADO and self.valor_final is not None:
            return self.valor_final
        return self.valor_previsto + (self.multa_atraso or Decimal("0"))

    @property
    def atrasada(self):
        from django.utils import timezone

        if self.status != self.Status.ATIVO:
            return False
        return timezone.now() > self.data_prevista_devolucao

    @property
    def status_color(self):
        if self.status == self.Status.ENCERRADO:
            return "gray"
        return "red" if self.atrasada else "blue"
