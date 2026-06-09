from django.contrib.auth.models import User
from django.db import models

from apps.common.models import TimeStampedModel


class Profile(TimeStampedModel):
    """Perfil que estende o usuário do Django com um papel de acesso."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        OPERADOR = "operador", "Operador"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="usuário",
    )
    role = models.CharField(
        "perfil de acesso",
        max_length=20,
        choices=Role.choices,
        default=Role.OPERADOR,
        db_index=True,
    )
    telefone = models.CharField("telefone", max_length=20, blank=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfis"

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """Administrador OU superusuário têm acesso total."""
        return self.role == self.Role.ADMIN or self.user.is_superuser
