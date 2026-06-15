from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ConfiguracaoForm
from .models import Configuracao


class ConfiguracaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Configuracao
    form_class = ConfiguracaoForm
    template_name = "configuracao/form.html"
    success_url = reverse_lazy("configuracao:editar")

    def get_object(self, queryset=None):
        return Configuracao.get_solo()

    def form_valid(self, form):
        messages.success(self.request, "Configurações salvas.")
        return super().form_valid(form)
