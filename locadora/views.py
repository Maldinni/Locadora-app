"""View do dashboard (página inicial)."""
import json
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.locacoes.models import Locacao
from apps.veiculos.models import Veiculo

MESES_PT = [
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
]


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoje = timezone.localdate()

        # ---- Cards de contagem ----
        veiculos = Veiculo.objects.all()
        ctx["total_veiculos"] = veiculos.count()
        ctx["disponiveis"] = veiculos.filter(status=Veiculo.Status.DISPONIVEL).count()
        ctx["alugados"] = veiculos.filter(status=Veiculo.Status.ALUGADO).count()
        ctx["em_manutencao"] = veiculos.filter(status=Veiculo.Status.MANUTENCAO).count()

        # ---- Receita do mês corrente ----
        inicio_mes = hoje.replace(day=1)
        locacoes_mes = Locacao.objects.filter(
            data_retirada__date__gte=inicio_mes, data_retirada__date__lte=hoje
        )
        ctx["receita_mes"] = sum(
            (loc.valor_total for loc in locacoes_mes), Decimal("0.00")
        )

        # ---- Próximos 5 vencimentos (IPVA ou seguro, próximos 30 dias) ----
        limite = hoje + timedelta(days=30)
        vencimentos = []
        for v in veiculos:
            for tipo, data_venc in (
                ("IPVA", v.vencimento_ipva),
                ("Seguro", v.vencimento_seguro),
            ):
                if data_venc and hoje <= data_venc <= limite:
                    vencimentos.append(
                        {
                            "veiculo": v,
                            "tipo": tipo,
                            "data": data_venc,
                            "dias": (data_venc - hoje).days,
                        }
                    )
        vencimentos.sort(key=lambda x: x["data"])
        ctx["vencimentos"] = vencimentos[:5]

        # ---- Próximas 3 revisões preventivas (por quilometragem) ----
        revisoes = []
        for v in veiculos:
            registro = v.proxima_revisao()
            if registro and registro.proxima_revisao_km:
                km_restante = registro.proxima_revisao_km - v.quilometragem_atual
                pendente = km_restante <= 0
                # % de "consumo" do intervalo de revisão (base 15.000 km) para a
                # barra de progresso no dashboard.
                pct = 100 if pendente else max(6, min(100, round((1 - km_restante / 15000) * 100)))
                revisoes.append(
                    {
                        "veiculo": v,
                        "proxima_km": registro.proxima_revisao_km,
                        "km_restante": km_restante,
                        "pendente": pendente,
                        "pct": pct,
                    }
                )
        revisoes.sort(key=lambda x: x["km_restante"])
        ctx["revisoes"] = revisoes[:3]

        # ---- Gráfico: receita dos últimos 6 meses ----
        labels, valores = self._receita_ultimos_meses(hoje, meses=6)
        ctx["chart_labels"] = json.dumps(labels)
        ctx["chart_receita"] = json.dumps(valores)
        ctx["chart_status"] = json.dumps(
            [ctx["disponiveis"], ctx["alugados"], ctx["em_manutencao"]]
        )

        return ctx

    def _receita_ultimos_meses(self, hoje, meses=6):
        labels, valores = [], []
        ano, mes = hoje.year, hoje.month
        # Recua (meses-1) meses para começar.
        indices = []
        for i in range(meses - 1, -1, -1):
            m = mes - i
            a = ano
            while m <= 0:
                m += 12
                a -= 1
            indices.append((a, m))
        for a, m in indices:
            total = sum(
                (
                    loc.valor_total
                    for loc in Locacao.objects.filter(
                        data_retirada__year=a, data_retirada__month=m
                    )
                ),
                Decimal("0.00"),
            )
            labels.append(f"{MESES_PT[m - 1]}/{str(a)[2:]}")
            valores.append(float(total))
        return labels, valores
