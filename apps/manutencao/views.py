from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.veiculos.models import Veiculo

from .forms import ManutencaoForm
from .models import Manutencao


class ManutencaoListView(LoginRequiredMixin, ListView):
    model = Manutencao
    template_name = "manutencao/lista.html"
    context_object_name = "manutencoes"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("veiculo")
        veiculo_id = self.request.GET.get("veiculo", "").strip()
        if veiculo_id.isdigit():
            qs = qs.filter(veiculo_id=int(veiculo_id))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["veiculos"] = Veiculo.objects.all()
        ctx["veiculo_atual"] = self.request.GET.get("veiculo", "")
        return ctx


class _ManutencaoFormMixin:
    model = Manutencao
    form_class = ManutencaoForm
    template_name = "manutencao/form.html"
    success_url = reverse_lazy("manutencao:lista")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Mantém a km do veículo atualizada se o registro for mais recente.
        veiculo = self.object.veiculo
        if self.object.km_momento > veiculo.quilometragem_atual:
            veiculo.quilometragem_atual = self.object.km_momento
            veiculo.save(update_fields=["quilometragem_atual", "updated_at"])
        return response


class ManutencaoCreateView(LoginRequiredMixin, _ManutencaoFormMixin, CreateView):
    def form_valid(self, form):
        messages.success(self.request, "Manutenção registrada.")
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        veiculo_id = self.request.GET.get("veiculo", "")
        if veiculo_id.isdigit():
            initial["veiculo"] = int(veiculo_id)
        return initial


class ManutencaoUpdateView(LoginRequiredMixin, _ManutencaoFormMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, "Manutenção atualizada.")
        return super().form_valid(form)


class ManutencaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Manutencao
    template_name = "manutencao/confirmar_exclusao.html"
    success_url = reverse_lazy("manutencao:lista")

    def form_valid(self, form):
        messages.success(self.request, "Registro de manutenção excluído.")
        return super().form_valid(form)
