from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Conjunto de ícones (linha, traço 1.6px) — espelha app/icons.jsx do protótipo.
# Cada valor é um único atributo `d` (pode conter vários sub-traços "M ...").
ICON_PATHS = {
    "dashboard": "M3 12.5 12 4l9 8.5M5.5 10.7V20h13v-9.3M9.5 20v-5.5h5V20",
    "car": "M5 16.5h14M6 16.5v2M18 16.5v2M4.5 12.5l1.8-4.4A2 2 0 0 1 8.1 6.9h7.8a2 2 0 0 1 1.8 1.2l1.8 4.4M4.5 12.5h15v3.2a.8.8 0 0 1-.8.8H5.3a.8.8 0 0 1-.8-.8zM7 14.6h.01M17 14.6h.01",
    "users": "M16 19v-1.5a3.5 3.5 0 0 0-3.5-3.5h-4A3.5 3.5 0 0 0 5 17.5V19M10.5 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6M19 19v-1.4a3 3 0 0 0-2.2-2.9M15.5 5.2a3 3 0 0 1 0 5.6",
    "contract": "M7 3.5h7l4 4V20a.5.5 0 0 1-.5.5h-10A.5.5 0 0 1 7 20zM13.5 3.5V8h4M9.5 12.5h6M9.5 15.5h6M9.5 9.5h2",
    "wrench": "M14.7 6.3a3.7 3.7 0 0 0-4.9 4.6l-5.2 5.2a1.5 1.5 0 0 0 2.1 2.1l5.2-5.2a3.7 3.7 0 0 0 4.6-4.9l-2 2-2-2z",
    "alert": "M12 4.5 21 19.5H3zM12 10v4M12 17h.01",
    "chart": "M4 4v16h16M8 16v-4M12 16V9M16 16v-7M20 16v-2",
    "search": "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14M20 20l-4-4",
    "plus": "M12 5v14M5 12h14",
    "edit": "M4 20h4l10-10a2 2 0 0 0-3-3L5 17v3zM13.5 6.5l3 3",
    "trash": "M5 7h14M9.5 7V5.5a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1V7M7 7l.8 12a1 1 0 0 0 1 .9h6.4a1 1 0 0 0 1-.9L17 7M10.5 11v5M13.5 11v5",
    "refresh": "M19 8a7 7 0 0 0-12-2L5 8M5 4v4h4M5 16a7 7 0 0 0 12 2l2-2M19 20v-4h-4",
    "check": "M5 12.5 10 17l9-10",
    "checkCircle": "M21 12a9 9 0 1 1-2.6-6.3M9 12l2.5 2.5L21 5.5",
    "sun": "M12 6.5v-2M12 19.5v-2M5.5 12h-2M20.5 12h-2M7.4 7.4 6 6M18 18l-1.4-1.4M7.4 16.6 6 18M18 6l-1.4 1.4M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7",
    "moon": "M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5",
    "calendar": "M5 6.5h14a.5.5 0 0 1 .5.5v12a.5.5 0 0 1-.5.5H5a.5.5 0 0 1-.5-.5V7a.5.5 0 0 1 .5-.5M8 4.5v4M16 4.5v4M4.5 11h15",
    "clock": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18M12 7.5V12l3 2",
    "key": "M14 4a6 6 0 0 0-5.6 8.2L3 17.6V21h3.4l.6-.6V18h2v-2h2l1.4-1.4A6 6 0 1 0 14 4M16.5 8.5h.01",
    "gauge": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18M12 12l3.5-3.5M12 16.5a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1",
    "download": "M12 4v11M8 11l4 4 4-4M5 19.5h14",
    "coins": "M9 11.5a5.5 2.5 0 1 0 0-5 5.5 2.5 0 0 0 0 5M3.5 6.5v5c0 1.4 2.5 2.5 5.5 2.5s5.5-1.1 5.5-2.5v-5M15 13.5a5.5 2.5 0 1 0 0-5M20.5 11v5c0 1.4-2.5 2.5-5.5 2.5-1 0-2-.1-2.8-.4",
    "trend": "M4 16l5-5 3 3 7-7M15 7h5v5",
    "bell": "M18 9a6 6 0 1 0-12 0c0 5-2 6.5-2 6.5h16S18 14 18 9M13.7 19a2 2 0 0 1-3.4 0",
    "chevron": "M9 6l6 6-6 6",
    "chevronDown": "M6 9l6 6 6-6",
    "logout": "M9 5H5.5a.5.5 0 0 0-.5.5v13a.5.5 0 0 0 .5.5H9M15 16l4-4-4-4M19 12H9",
    "shield": "M12 3.5 19 6v5c0 4.5-3 7.8-7 9.5-4-1.7-7-5-7-9.5V6z",
    "receipt": "M6 3.5h12v17l-2.5-1.5L13 20.5 10.5 19 8 20.5 5.5 20V4a.5.5 0 0 1 .5-.5M9 8h6M9 11.5h6M9 15h4",
    "eye": "M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6",
    "menu": "M4 6h16M4 12h16M4 18h16",
    "x": "M6 6l12 12M18 6 6 18",
    "lock": "M6 10.5h12a.5.5 0 0 1 .5.5v8a.5.5 0 0 1-.5.5H6a.5.5 0 0 1-.5-.5v-8a.5.5 0 0 1 .5-.5M8 10.5V8a4 4 0 0 1 8 0v2.5",
    "settings": "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z",
}

# Mapeia os tokens de cor antigos dos models (status_color) para os tons do design.
COLOR_TONE = {
    "green": "success", "blue": "info", "red": "danger",
    "yellow": "warning", "orange": "warning", "gray": "neutral",
}


@register.simple_tag
def icon(name, size=18, css="", stroke=1.6):
    """Renderiza um ícone SVG do conjunto. Uso: {% icon "car" 20 "nav__ico-svg" %}"""
    d = ICON_PATHS.get(name)
    if not d:
        return ""
    return format_html(
        '<svg width="{}" height="{}" viewBox="0 0 24 24" fill="none" class="{}" '
        'aria-hidden="true" stroke="currentColor" stroke-width="{}" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="{}"/></svg>',
        size, size, css, stroke, mark_safe(d),
    )


@register.filter
def tone(color):
    """Converte um token de cor do model (green/blue/red/...) em tom do design."""
    return COLOR_TONE.get(color, "neutral")


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
