from django.db import models

from apps.common.models import TimeStampedModel


class Configuracao(TimeStampedModel):
    """Configuração única da locadora (dados do LOCADOR usados no contrato).

    É um *singleton*: existe sempre uma só linha (pk=1). Use
    ``Configuracao.get_solo()`` para obtê-la/criá-la.
    """

    nome_locador = models.CharField("nome do locador", max_length=150, blank=True)
    cpf_locador = models.CharField("CPF/CNPJ do locador", max_length=20, blank=True)
    endereco_locador = models.CharField("endereço do locador", max_length=255, blank=True)

    class Meta:
        verbose_name = "configuração"
        verbose_name_plural = "configurações"

    def __str__(self):
        return self.nome_locador or "Configuração da locadora"

    def save(self, *args, **kwargs):
        # Garante o singleton: sempre pk=1.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
