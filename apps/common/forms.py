"""Utilitários compartilhados de formulários."""
from django import forms

# Classes do design system (ver static/css/custom.css).
INPUT_CLASSES = "form-control"
CHECKBOX_CLASSES = "form-check"


class TailwindStyledFormMixin:
    """Aplica as classes do design system a todos os widgets do formulário.

    Use herdando antes de forms.Form / forms.ModelForm:

        class MeuForm(TailwindStyledFormMixin, forms.ModelForm):
            ...
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                self._add_class(widget, CHECKBOX_CLASSES)
            elif isinstance(widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)):
                continue
            else:
                self._add_class(widget, INPUT_CLASSES)
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 3)
            # Datas e horas ganham o input nativo apropriado.
            if isinstance(widget, forms.DateInput):
                widget.input_type = "date"
            elif isinstance(widget, forms.DateTimeInput):
                widget.input_type = "datetime-local"

    @staticmethod
    def _add_class(widget, css):
        existing = widget.attrs.get("class", "")
        widget.attrs["class"] = (existing + " " + css).strip()
