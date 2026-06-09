"""Cálculos do relatório financeiro."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from django.db.models import Sum

from apps.locacoes.models import Locacao
from apps.manutencao.models import Manutencao
from apps.veiculos.models import Veiculo


@dataclass
class RelatorioFinanceiro:
    inicio: date
    fim: date
    locacoes: list = field(default_factory=list)
    receita: Decimal = Decimal("0.00")
    custo_manutencao: Decimal = Decimal("0.00")
    total_parcelas: Decimal = Decimal("0.00")
    meses_no_periodo: int = 1

    @property
    def lucro_estimado(self):
        return self.receita - self.custo_manutencao - self.total_parcelas


def _meses_no_periodo(inicio, fim):
    return (fim.year - inicio.year) * 12 + (fim.month - inicio.month) + 1


def montar_relatorio(inicio: date, fim: date) -> RelatorioFinanceiro:
    rel = RelatorioFinanceiro(inicio=inicio, fim=fim)

    # Contratos com retirada dentro do período.
    locacoes = (
        Locacao.objects.select_related("cliente", "veiculo")
        .filter(data_retirada__date__gte=inicio, data_retirada__date__lte=fim)
        .order_by("data_retirada")
    )
    rel.locacoes = list(locacoes)
    rel.receita = sum((loc.valor_total for loc in rel.locacoes), Decimal("0.00"))

    # Custos de manutenção no período.
    rel.custo_manutencao = Manutencao.objects.filter(
        data__gte=inicio, data__lte=fim
    ).aggregate(total=Sum("custo"))["total"] or Decimal("0.00")

    # Parcelas (financiamento) no período: soma mensal × nº de meses.
    parcela_mensal = Veiculo.objects.filter(valor_parcela__isnull=False).aggregate(
        total=Sum("valor_parcela")
    )["total"] or Decimal("0.00")
    rel.meses_no_periodo = max(1, _meses_no_periodo(inicio, fim))
    rel.total_parcelas = parcela_mensal * rel.meses_no_periodo

    return rel
