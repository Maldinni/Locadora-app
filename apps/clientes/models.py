from datetime import date

from django.db import models
from django.urls import reverse

from apps.common.models import TimeStampedModel

from .validators import validate_cpf


class Cliente(TimeStampedModel):
    UFS = [
        ("AC", "AC"), ("AL", "AL"), ("AP", "AP"), ("AM", "AM"), ("BA", "BA"),
        ("CE", "CE"), ("DF", "DF"), ("ES", "ES"), ("GO", "GO"), ("MA", "MA"),
        ("MT", "MT"), ("MS", "MS"), ("MG", "MG"), ("PA", "PA"), ("PB", "PB"),
        ("PR", "PR"), ("PE", "PE"), ("PI", "PI"), ("RJ", "RJ"), ("RN", "RN"),
        ("RS", "RS"), ("RO", "RO"), ("RR", "RR"), ("SC", "SC"), ("SP", "SP"),
        ("SE", "SE"), ("TO", "TO"),
    ]

    nome = models.CharField("nome completo", max_length=150)
    cpf = models.CharField(
        "CPF", max_length=11, unique=True, db_index=True, validators=[validate_cpf]
    )
    cnh = models.CharField("número da CNH", max_length=20)
    validade_cnh = models.DateField("validade da CNH")
    telefone = models.CharField("telefone", max_length=20)
    email = models.EmailField("e-mail", blank=True)

    # Endereço
    logradouro = models.CharField("logradouro", max_length=150)
    numero = models.CharField("número", max_length=10)
    complemento = models.CharField("complemento", max_length=80, blank=True)
    bairro = models.CharField("bairro", max_length=80)
    cidade = models.CharField("cidade", max_length=80)
    uf = models.CharField("UF", max_length=2, choices=UFS)
    cep = models.CharField("CEP", max_length=9)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.cpf_formatado})"

    def get_absolute_url(self):
        return reverse("clientes:detalhe", args=[self.pk])

    @property
    def cpf_formatado(self):
        c = self.cpf
        if len(c) == 11:
            return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"
        return c

    @property
    def cnh_vencida(self):
        return self.validade_cnh < date.today()

    @property
    def endereco_completo(self):
        partes = [f"{self.logradouro}, {self.numero}"]
        if self.complemento:
            partes.append(self.complemento)
        partes.append(f"{self.bairro} — {self.cidade}/{self.uf}")
        partes.append(f"CEP {self.cep}")
        return " · ".join(partes)
