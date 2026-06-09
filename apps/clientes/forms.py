from django import forms

from apps.common.forms import TailwindStyledFormMixin

from .models import Cliente
from .validators import so_digitos


class ClienteForm(TailwindStyledFormMixin, forms.ModelForm):
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
            "cpf": forms.TextInput(attrs={"placeholder": "000.000.000-00"}),
        }

    def clean_cpf(self):
        # Normaliza para somente dígitos; o validador do model confere os DVs.
        return so_digitos(self.cleaned_data["cpf"])
