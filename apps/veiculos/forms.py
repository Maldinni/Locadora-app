from django import forms

from apps.common.forms import TailwindStyledFormMixin

from .models import Veiculo


class VeiculoForm(TailwindStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            "marca",
            "modelo",
            "ano",
            "placa",
            "quilometragem_atual",
            "status",
            "categoria",
            "valor_compra",
            "valor_parcela",
            "qtd_parcelas",
            "vencimento_ipva",
            "vencimento_seguro",
            "observacoes",
            "manutencao_motivo",
            "manutencao_retorno_previsto",
        ]
        widgets = {
            "vencimento_ipva": forms.DateInput(),
            "vencimento_seguro": forms.DateInput(),
            "manutencao_retorno_previsto": forms.DateInput(),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_placa(self):
        return self.cleaned_data["placa"].upper().replace("-", "").replace(" ", "")

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        motivo = cleaned.get("manutencao_motivo")
        if status == Veiculo.Status.MANUTENCAO and not motivo:
            self.add_error(
                "manutencao_motivo",
                "Informe o motivo ao colocar o veículo em manutenção.",
            )
        return cleaned
