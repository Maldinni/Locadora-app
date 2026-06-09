from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import MultaForm
from .models import Multa


class MultaListView(LoginRequiredMixin, ListView):
    model = Multa
    template_name = "multas/lista.html"
    context_object_name = "multas"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("veiculo", "contrato__cliente")
        status = self.request.GET.get("status", "").strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Multa.Status.choices
        ctx["status_atual"] = self.request.GET.get("status", "")
        return ctx


class MultaCreateView(LoginRequiredMixin, CreateView):
    model = Multa
    form_class = MultaForm
    template_name = "multas/form.html"
    success_url = reverse_lazy("multas:lista")

    def form_valid(self, form):
        messages.success(self.request, "Multa registrada.")
        return super().form_valid(form)


class MultaUpdateView(LoginRequiredMixin, UpdateView):
    model = Multa
    form_class = MultaForm
    template_name = "multas/form.html"
    success_url = reverse_lazy("multas:lista")

    def form_valid(self, form):
        messages.success(self.request, "Multa atualizada.")
        return super().form_valid(form)


class MultaDeleteView(LoginRequiredMixin, DeleteView):
    model = Multa
    template_name = "multas/confirmar_exclusao.html"
    success_url = reverse_lazy("multas:lista")

    def form_valid(self, form):
        messages.success(self.request, "Multa excluída.")
        return super().form_valid(form)
