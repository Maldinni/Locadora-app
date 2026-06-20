"""View do dashboard (página inicial)."""
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.veiculos.models import Veiculo


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

        # ---- Próximos 5 vencimentos de IPVA (próximos 30 dias) ----
        limite = hoje + timedelta(days=30)
        vencimentos = []
        for v in veiculos:
            for tipo, data_venc in (
                ("IPVA", v.vencimento_ipva),
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

        return ctx
