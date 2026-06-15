from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
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
from .services import gerar_contrato


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


def _liberar_locacao(locacao):
    """Marca a locação como ativa (liberada) e o veículo como alugado."""
    locacao.status = Locacao.Status.ATIVO
    locacao.save(update_fields=["status", "updated_at"])
    veiculo = locacao.veiculo
    veiculo.status = Veiculo.Status.ALUGADO
    veiculo.save(update_fields=["status", "updated_at"])


class LocacaoCreateView(LoginRequiredMixin, CreateView):
    model = Locacao
    form_class = LocacaoForm
    template_name = "locacoes/form.html"

    @transaction.atomic
    def form_valid(self, form):
        # Nasce aguardando contrato; só é liberada quando o contrato é gerado.
        form.instance.status = Locacao.Status.PENDENTE
        response = super().form_valid(form)
        try:
            gerar_contrato(self.object)
        except Exception as exc:  # noqa: BLE001
            messages.warning(
                self.request,
                "Locação registrada como 'Aguardando contrato', mas o contrato não "
                f"pôde ser gerado ({exc}). Use 'Gerar contrato' na tela da locação.",
            )
            return response
        # Contrato gerado → libera a locação e marca o veículo como alugado.
        _liberar_locacao(self.object)
        messages.success(
            self.request,
            "Locação registrada e liberada. Contrato gerado e veículo marcado como alugado.",
        )
        return response


class GerarContratoView(LoginRequiredMixin, View):
    """(Re)gera o contrato de uma locação e a libera, se ainda estiver pendente."""

    @transaction.atomic
    def post(self, request, pk):
        locacao = get_object_or_404(Locacao, pk=pk)
        if locacao.status == Locacao.Status.ENCERRADO:
            messages.info(request, "Locação encerrada — contrato não pode ser gerado.")
            return redirect(locacao.get_absolute_url())
        try:
            gerar_contrato(locacao)
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Não foi possível gerar o contrato: {exc}")
            return redirect(locacao.get_absolute_url())
        if locacao.status == Locacao.Status.PENDENTE:
            _liberar_locacao(locacao)
            messages.success(request, "Contrato gerado. Locação liberada e veículo alugado.")
        else:
            messages.success(request, "Contrato gerado novamente.")
        return redirect(locacao.get_absolute_url())


class BaixarContratoView(LoginRequiredMixin, View):
    """Faz o download do contrato pelo Django (protegido por login).

    Evita expor os arquivos de ``media/`` publicamente — o contrato tem dados
    pessoais do cliente (CPF, endereço) — e dispensa o mapeamento de /media/.
    """

    def get(self, request, pk):
        locacao = get_object_or_404(Locacao, pk=pk)
        if not locacao.contrato:
            raise Http404("Contrato ainda não gerado para esta locação.")
        return FileResponse(
            locacao.contrato.open("rb"),
            as_attachment=True,
            filename=f"contrato_locacao_{locacao.pk}.docx",
        )


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
