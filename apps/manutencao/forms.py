from django import forms

from apps.common.forms import TailwindStyledFormMixin

from .models import Manutencao


class ManutencaoForm(TailwindStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = [
            "veiculo",
            "tipo_servico",
            "descricao",
            "data",
            "custo",
            "km_momento",
            "proxima_revisao_km",
            "proxima_revisao_data",
        ]
        widgets = {
            "data": forms.DateInput(),
            "proxima_revisao_data": forms.DateInput(),
            "descricao": forms.Textarea(attrs={"rows": 3}),
        }
