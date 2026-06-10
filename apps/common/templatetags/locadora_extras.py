from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """Retorna a query string atual com os parâmetros informados sobrescritos.

    Uso: <a href="?{% querystring page=3 %}">  — preserva os demais filtros.
    """
    request = context.get("request")
    params = request.GET.copy() if request else {}
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = value
    encoded = params.urlencode()
    return encoded


@register.filter
def brl(value):
    """Formata um número como moeda brasileira (R$ 1.234,56)."""
    try:
        valor = float(value)
    except (TypeError, ValueError):
        return value
    inteiro, decimal = f"{valor:,.2f}".split(".")
    inteiro = inteiro.replace(",", ".")
    return f"R$ {inteiro},{decimal}"
