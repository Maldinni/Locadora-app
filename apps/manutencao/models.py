from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel


class Manutencao(TimeStampedModel):
    class Tipo(models.TextChoices):
        OLEO = "oleo", "Troca de óleo"
        REVISAO = "revisao", "Revisão"
        PNEUS = "pneus", "Pneus"
        FREIOS = "freios", "Freios"
        OUTRO = "outro", "Outro"

    veiculo = models.ForeignKey(
        "veiculos.Veiculo",
        on_delete=models.CASCADE,
        related_name="manutencoes",
        verbose_name="veículo",
    )
    tipo_servico = models.CharField(
        "tipo de serviço", max_length=20, choices=Tipo.choices, db_index=True
    )
    descricao = models.TextField("descrição", blank=True)
    data = models.DateField("data")
    custo = models.DecimalField("custo", max_digits=10, decimal_places=2, default=0)
    km_momento = models.PositiveIntegerField("quilometragem no momento")

    proxima_revisao_km = models.PositiveIntegerField(
        "próxima revisão (km)", null=True, blank=True
    )
    proxima_revisao_data = models.DateField(
        "próxima revisão (data)", null=True, blank=True
    )

    class Meta:
        verbose_name = "manutenção"
        verbose_name_plural = "manutenções"
        ordering = ["-data"]
        indexes = [models.Index(fields=["veiculo", "-data"])]

    def __str__(self):
        return f"{self.get_tipo_servico_display()} — {self.veiculo.placa} ({self.data})"

    def get_absolute_url(self):
        return reverse("manutencao:lista")
