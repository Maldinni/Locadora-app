from django import forms

from apps.common.forms import TailwindStyledFormMixin

from .models import Multa


class MultaForm(TailwindStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Multa
        fields = [
            "veiculo",
            "contrato",
            "data_infracao",
            "valor",
            "descricao",
            "status",
        ]
        widgets = {"data_infracao": forms.DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contrato"].required = False
        self.fields["contrato"].empty_label = "— sem contrato —"
