"""Modelos base reutilizáveis."""
from django.db import models


class TimeStampedModel(models.Model):
    """Adiciona created_at / updated_at automáticos a qualquer model."""

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True
