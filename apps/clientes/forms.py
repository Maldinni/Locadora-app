from django import forms

from apps.common.forms import TailwindStyledFormMixin

from .models import Cliente
from .validators import so_digitos


class ClienteForm(TailwindStyledFormMixin, forms.ModelForm):
    # Aceita CPF com máscara (14 chars); clean_cpf normaliza para 11 dígitos
    # antes de salvar, então o max_length=11 do model não pode barrar a entrada.
    cpf = forms.CharField(
        label="CPF",
        max_length=14,
        widget=forms.TextInput(attrs={"placeholder": "000.000.000-00"}),
    )

    class Meta:
        model = Cliente
        fields = [
            "nome",
            "cpf",
            "cnh",
            "validade_cnh",
            "telefone",
            "email",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "uf",
            "cep",
        ]
        widgets = {
            "validade_cnh": forms.DateInput(),
        }

    def clean_cpf(self):
        # Normaliza para somente dígitos; o validador do model confere os DVs.
        return so_digitos(self.cleaned_data["cpf"])
