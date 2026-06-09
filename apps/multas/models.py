from django.db import models

from apps.common.models import TimeStampedModel


class Multa(TimeStampedModel):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        PAGO = "pago", "Pago"
        CONTESTADO = "contestado", "Contestado"

    veiculo = models.ForeignKey(
        "veiculos.Veiculo",
        on_delete=models.CASCADE,
        related_name="multas",
        verbose_name="veículo",
    )
    contrato = models.ForeignKey(
        "locacoes.Locacao",
        on_delete=models.SET_NULL,
        related_name="multas",
        null=True,
        blank=True,
        verbose_name="contrato associado",
    )
    data_infracao = models.DateField("data da infração")
    valor = models.DecimalField("valor", max_digits=10, decimal_places=2)
    descricao = models.CharField("descrição", max_length=255)
    status = models.CharField(
        "status", max_length=20, choices=Status.choices, default=Status.PENDENTE, db_index=True
    )

    class Meta:
        verbose_name = "multa"
        verbose_name_plural = "multas"
        ordering = ["-data_infracao"]

    def __str__(self):
        return f"Multa {self.veiculo.placa} — {self.data_infracao} (R$ {self.valor})"

    @property
    def cliente_responsavel(self):
        """Cliente responsável quando há contrato associado."""
        return self.contrato.cliente if self.contrato_id else None

    @property
    def status_color(self):
        return {
            self.Status.PENDENTE: "yellow",
            self.Status.PAGO: "green",
            self.Status.CONTESTADO: "red",
        }.get(self.status, "gray")
