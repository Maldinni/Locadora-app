from django import forms

from apps.common.forms import TailwindStyledFormMixin

from .models import Configuracao


class ConfiguracaoForm(TailwindStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ["nome_locador", "cpf_locador", "endereco_locador"]
