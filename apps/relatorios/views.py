import csv
from datetime import date

from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic.base import View

from apps.accounts.mixins import AdminRequiredMixin

from .services import montar_relatorio


def _periodo_do_request(request):
    """Lê início/fim do GET; padrão = mês corrente."""
    hoje = timezone.localdate()
    primeiro_dia = hoje.replace(day=1)

    def parse(nome, padrao):
        valor = request.GET.get(nome, "").strip()
        if valor:
            try:
                return date.fromisoformat(valor)
            except ValueError:
                pass
        return padrao

    inicio = parse("inicio", primeiro_dia)
    fim = parse("fim", hoje)
    if fim < inicio:
        inicio, fim = fim, inicio
    return inicio, fim


class RelatorioFinanceiroView(AdminRequiredMixin, TemplateView):
    template_name = "relatorios/financeiro.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        inicio, fim = _periodo_do_request(self.request)
        ctx["relatorio"] = montar_relatorio(inicio, fim)
        ctx["inicio"] = inicio
        ctx["fim"] = fim
        return ctx


class RelatorioCSVView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        inicio, fim = _periodo_do_request(request)
        rel = montar_relatorio(inicio, fim)

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorio_{inicio}_a_{fim}.csv"'
        )
        response.write("﻿")  # BOM para abrir certinho no Excel
        writer = csv.writer(response, delimiter=";")

        writer.writerow(["Relatório financeiro", f"{inicio} a {fim}"])
        writer.writerow([])
        writer.writerow(
            ["Locação", "Cliente", "Veículo", "Retirada", "Devolução", "Status", "Valor cobrado (R$)"]
        )
        for loc in rel.locacoes:
            writer.writerow(
                [
                    loc.pk,
                    loc.cliente.nome,
                    loc.veiculo.placa,
                    timezone.localtime(loc.data_retirada).strftime("%d/%m/%Y %H:%M"),
                    timezone.localtime(loc.data_devolucao_real).strftime("%d/%m/%Y %H:%M")
                    if loc.data_devolucao_real
                    else "-",
                    loc.get_status_display(),
                    f"{loc.valor_total:.2f}",
                ]
            )
        writer.writerow([])
        writer.writerow(["Receita do período (R$)", f"{rel.receita:.2f}"])
        writer.writerow(["Custos de manutenção (R$)", f"{rel.custo_manutencao:.2f}"])
        writer.writerow(
            [f"Parcelas ({rel.meses_no_periodo} mês/meses) (R$)", f"{rel.total_parcelas:.2f}"]
        )
        writer.writerow(["Lucro estimado (R$)", f"{rel.lucro_estimado:.2f}"])
        return response
