"""Geração automática do contrato de locação (.docx)."""
from __future__ import annotations

import io
from decimal import Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from num2words import num2words

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _moeda(valor: Decimal) -> str:
    """Formata como 1.234,56 (sem o prefixo R$, que já está no template)."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _por_extenso(valor: Decimal) -> str:
    """Valor por extenso, sem a palavra 'reais' (o template já a tem)."""
    reais = int(valor)
    centavos = int((valor - reais) * 100)
    texto = num2words(reais, lang="pt")
    if centavos:
        texto += f" e {num2words(centavos, lang='pt')} centavos"
    return texto


def _contexto(locacao, tpl: DocxTemplate) -> dict:
    cliente = locacao.cliente
    veiculo = locacao.veiculo
    config = _config()

    # Aluguel cobrado semanalmente (a cláusula 11 prevê pagamento semanal).
    valor_semanal = (locacao.valor_diaria or Decimal("0")) * 7

    inicio = timezone.localtime(locacao.data_retirada)
    hoje = timezone.localtime(timezone.now())

    logo = ""
    if settings.LOGO_PATH.exists():
        logo = InlineImage(tpl, str(settings.LOGO_PATH), width=Mm(40))

    return {
        "logo": logo,
        "locador_nome": config.nome_locador,
        "locador_cpf": config.cpf_locador,
        "locador_endereco": config.endereco_locador,
        "locatario_nome": cliente.nome,
        "locatario_cpf": cliente.cpf_formatado,
        "locatario_endereco": cliente.endereco_completo,
        "veiculo_marca": f"{veiculo.marca} {veiculo.modelo}",
        "veiculo_ano": veiculo.ano,
        "veiculo_placa": veiculo.placa,
        "inicio_dia": inicio.day,
        "inicio_mes": MESES[inicio.month - 1],
        "inicio_ano": inicio.year,
        "valor_num": _moeda(valor_semanal),
        "valor_extenso": _por_extenso(valor_semanal),
        "assin_dia": hoje.day,
        "assin_mes": MESES[hoje.month - 1],
        "assin_ano": hoje.year,
    }


def _config():
    # Import tardio para evitar dependência circular entre apps.
    from apps.configuracao.models import Configuracao

    return Configuracao.get_solo()


def render_contrato(locacao) -> ContentFile:
    """Renderiza o contrato preenchido e devolve um arquivo em memória."""
    tpl = DocxTemplate(str(settings.CONTRATO_TEMPLATE))
    tpl.render(_contexto(locacao, tpl))
    buffer = io.BytesIO()
    tpl.save(buffer)
    nome = f"contrato_locacao_{locacao.pk}.docx"
    return ContentFile(buffer.getvalue(), name=nome)


def gerar_contrato(locacao):
    """Gera o contrato e o anexa à locação (salvando o arquivo e a data)."""
    arquivo = render_contrato(locacao)
    locacao.contrato.save(arquivo.name, arquivo, save=False)
    locacao.contrato_gerado_em = timezone.now()
    locacao.save(update_fields=["contrato", "contrato_gerado_em", "updated_at"])
    return locacao
