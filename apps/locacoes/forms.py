from django import forms

from apps.common.forms import TailwindStyledFormMixin
from apps.veiculos.models import Veiculo

from .models import Locacao


class LocacaoForm(TailwindStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Locacao
        fields = [
            "cliente",
            "veiculo",
            "data_retirada",
            "data_prevista_devolucao",
            "valor_diaria",
            "km_saida",
            "forma_pagamento",
            "observacoes",
        ]
        widgets = {
            "data_retirada": forms.DateTimeInput(),
            "data_prevista_devolucao": forms.DateTimeInput(),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Só veículos disponíveis — mas mantém o já selecionado ao editar.
        disponiveis = Veiculo.objects.filter(status=Veiculo.Status.DISPONIVEL)
        if self.instance and self.instance.pk and self.instance.veiculo_id:
            disponiveis = disponiveis | Veiculo.objects.filter(pk=self.instance.veiculo_id)
        self.fields["veiculo"].queryset = disponiveis.distinct()

    def clean(self):
        cleaned = super().clean()
        cliente = cleaned.get("cliente")
        veiculo = cleaned.get("veiculo")
        retirada = cleaned.get("data_retirada")
        prevista = cleaned.get("data_prevista_devolucao")
        km_saida = cleaned.get("km_saida")

        if cliente and cliente.cnh_vencida:
            self.add_error(
                "cliente",
                "CNH do cliente está vencida — não é possível abrir contrato.",
            )

        if retirada and prevista and prevista <= retirada:
            self.add_error(
                "data_prevista_devolucao",
                "A devolução prevista deve ser posterior à retirada.",
            )

        # Bloqueia veículo já alugado (exceto se for o mesmo da edição).
        if veiculo and veiculo.status != Veiculo.Status.DISPONIVEL:
            editando_mesmo = (
                self.instance.pk and self.instance.veiculo_id == veiculo.pk
            )
            if not editando_mesmo:
                self.add_error("veiculo", "Este veículo não está disponível.")

        if veiculo and km_saida is not None and km_saida < veiculo.quilometragem_atual:
            self.add_error(
                "km_saida",
                f"Km de saída não pode ser menor que a atual do veículo "
                f"({veiculo.quilometragem_atual}).",
            )
        return cleaned


class DevolucaoForm(TailwindStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Locacao
        fields = ["data_devolucao_real", "km_retorno", "valor_final", "multa_atraso"]
        widgets = {"data_devolucao_real": forms.DateTimeInput()}

    def clean(self):
        cleaned = super().clean()
        data_real = cleaned.get("data_devolucao_real")
        km_retorno = cleaned.get("km_retorno")

        if data_real and data_real < self.instance.data_retirada:
            self.add_error(
                "data_devolucao_real",
                "A devolução não pode ser anterior à retirada.",
            )
        if km_retorno is not None and km_retorno < self.instance.km_saida:
            self.add_error(
                "km_retorno",
                f"Km de retorno não pode ser menor que a de saída "
                f"({self.instance.km_saida}).",
            )
        return cleaned
