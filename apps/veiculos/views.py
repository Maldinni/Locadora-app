from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.base import View

from .forms import VeiculoForm
from .models import Veiculo


class VeiculoListView(LoginRequiredMixin, ListView):
    model = Veiculo
    template_name = "veiculos/lista.html"
    context_object_name = "veiculos"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.GET.get("status", "").strip()
        busca = self.request.GET.get("q", "").strip()
        if status:
            qs = qs.filter(status=status)
        if busca:
            qs = qs.filter(Q(placa__icontains=busca) | Q(modelo__icontains=busca))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Veiculo.Status.choices
        ctx["status_atual"] = self.request.GET.get("status", "")
        ctx["busca"] = self.request.GET.get("q", "")
        return ctx


class VeiculoDetailView(LoginRequiredMixin, DetailView):
    model = Veiculo
    template_name = "veiculos/detalhe.html"
    context_object_name = "veiculo"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["manutencoes"] = self.object.manutencoes.order_by("-data")[:10]
        ctx["locacoes"] = self.object.locacoes.order_by("-data_retirada")[:10]
        return ctx


class VeiculoCreateView(LoginRequiredMixin, CreateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = "veiculos/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Veículo cadastrado com sucesso.")
        return super().form_valid(form)


class VeiculoUpdateView(LoginRequiredMixin, UpdateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = "veiculos/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Veículo atualizado com sucesso.")
        return super().form_valid(form)


class VeiculoDeleteView(LoginRequiredMixin, DeleteView):
    model = Veiculo
    template_name = "veiculos/confirmar_exclusao.html"
    success_url = reverse_lazy("veiculos:lista")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Não é possível excluir: o veículo possui locações ou registros vinculados.",
            )
            return self.get(self.request, *self.args, **self.kwargs)
        messages.success(self.request, "Veículo excluído.")
        return response


class VeiculoStatusView(LoginRequiredMixin, View):
    """Troca rápida de status via HTMX (retorna o badge atualizado)."""

    def post(self, request, pk):
        veiculo = get_object_or_404(Veiculo, pk=pk)
        novo = request.POST.get("status", "")
        motivo = request.POST.get("manutencao_motivo", "").strip()
        retorno = request.POST.get("manutencao_retorno_previsto", "").strip()

        if novo not in Veiculo.Status.values:
            messages.error(request, "Status inválido.")
        elif veiculo.status == Veiculo.Status.ALUGADO:
            messages.error(
                request,
                "Veículo alugado: registre a devolução da locação para liberar.",
            )
        elif novo == Veiculo.Status.ALUGADO:
            messages.error(request, "Para marcar como alugado, registre uma locação.")
        elif novo == Veiculo.Status.MANUTENCAO and not motivo:
            messages.error(request, "Informe o motivo da manutenção.")
        else:
            veiculo.status = novo
            if novo == Veiculo.Status.MANUTENCAO:
                veiculo.manutencao_motivo = motivo
                veiculo.manutencao_retorno_previsto = parse_date(retorno) if retorno else None
            else:
                veiculo.manutencao_motivo = ""
                veiculo.manutencao_retorno_previsto = None
            veiculo.save()
            messages.success(request, "Status atualizado.")

        return render(
            request,
            "veiculos/partials/status_control.html",
            {"veiculo": veiculo, "com_oob_toast": True},
        )
