from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from apps.common.forms import INPUT_CLASSES


class TailwindAuthenticationForm(AuthenticationForm):
    """Form de login com widgets estilizados."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": INPUT_CLASSES, "placeholder": "Usuário", "autofocus": True}
        )
        self.fields["password"].widget.attrs.update(
            {"class": INPUT_CLASSES, "placeholder": "Senha"}
        )


class TailwindPasswordChangeForm(PasswordChangeForm):
    """Form de troca de senha com widgets estilizados."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": INPUT_CLASSES})
