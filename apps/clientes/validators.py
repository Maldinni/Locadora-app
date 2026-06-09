"""Validação de CPF com dígitos verificadores."""
import re

from django.core.exceptions import ValidationError


def so_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def validate_cpf(valor):
    """Valida CPF pelos dígitos verificadores (aceita com ou sem máscara)."""
    cpf = so_digitos(valor)

    if len(cpf) != 11:
        raise ValidationError("CPF deve conter 11 dígitos.")

    # Rejeita sequências repetidas (000..., 111..., etc.).
    if cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido.")

    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * ((tamanho + 1) - i) for i in range(tamanho))
        resto = (soma * 10) % 11
        digito = 0 if resto == 10 else resto
        if digito != int(cpf[tamanho]):
            raise ValidationError("CPF inválido.")
    return cpf
