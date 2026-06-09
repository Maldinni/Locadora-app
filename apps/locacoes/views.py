from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.veiculos.models import Veiculo

from .forms import DevolucaoForm, LocacaoForm
from .models import Locacao


class LocacaoListView(LoginRequiredMixin, ListView):
    model = Locacao
    template_name = "locacoes/lista.html"
    context_object_name = "locacoes"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("cliente", "veiculo")
        status = self.request.GET.get("status", "").strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Locacao.Status.choices
        ctx["status_atual"] = self.request.GET.get("status", "")
        return ctx


class LocacaoDetailView(LoginRequiredMixin, DetailView):
    model = Locacao
    template_name = "locacoes/detalhe.html"
    context_object_name = "locacao"


class LocacaoCreateView(LoginRequiredMixin, CreateView):
    model = Locacao
    form_class = LocacaoForm
    template_name = "locacoes/form.html"

    @transaction.atomic
    def form_valid(self, form):
        form.instance.status = Locacao.Status.ATIVO
        response = super().form_valid(form)
        # Regra: ao abrir contrato, o veículo passa a "alugado".
        veiculo = self.object.veiculo
        veiculo.status = Veiculo.Status.ALUGADO
        veiculo.save(update_fields=["status", "updated_at"])
        messages.success(self.request, "Locação registrada. Veículo marcado como alugado.")
        return response


class LocacaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Locacao
    form_class = LocacaoForm
    template_name = "locacoes/form.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status == Locacao.Status.ENCERRADO:
            messages.error(request, "Locação encerrada não pode ser editada.")
            return redirect(obj.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Locação atualizada.")
        return super().form_valid(form)


class LocacaoDevolucaoView(LoginRequiredMixin, UpdateView):
    model = Locacao
    form_class = DevolucaoForm
    template_name = "locacoes/devolucao.html"
    context_object_name = "locacao"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status == Locacao.Status.ENCERRADO:
            messages.info(request, "Esta locação já foi encerrada.")
            return redirect(obj.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        obj = self.object
        return {
            "data_devolucao_real": timezone.now(),
            "multa_atraso": obj.multa_sugerida,
            "valor_final": obj.valor_previsto + obj.multa_sugerida,
        }

    @transaction.atomic
    def form_valid(self, form):
        form.instance.status = Locacao.Status.ENCERRADO
        response = super().form_valid(form)
        # Regra: ao devolver, veículo volta a "disponível" e atualiza km.
        veiculo = self.object.veiculo
        veiculo.status = Veiculo.Status.DISPONIVEL
        if self.object.km_retorno is not None:
            veiculo.quilometragem_atual = self.object.km_retorno
        veiculo.save(update_fields=["status", "quilometragem_atual", "updated_at"])
        messages.success(self.request, "Devolução registrada. Veículo disponível novamente.")
        return response


class LocacaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Locacao
    template_name = "locacoes/confirmar_exclusao.html"
    success_url = reverse_lazy("locacoes:lista")

    @transaction.atomic
    def form_valid(self, form):
        locacao = self.get_object()
        veiculo = locacao.veiculo
        response = super().form_valid(form)
        # Se a locação estava ativa, libera o veículo.
        if locacao.status == Locacao.Status.ATIVO and veiculo.status == Veiculo.Status.ALUGADO:
            veiculo.status = Veiculo.Status.DISPONIVEL
            veiculo.save(update_fields=["status", "updated_at"])
        messages.success(self.request, "Locação excluída.")
        return response
