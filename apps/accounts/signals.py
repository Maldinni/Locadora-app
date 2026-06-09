from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def criar_ou_atualizar_profile(sender, instance, created, **kwargs):
    """Garante que todo usuário tenha um Profile associado."""
    if created:
        # Superusuários criados via createsuperuser viram Administradores.
        role = Profile.Role.ADMIN if instance.is_superuser else Profile.Role.OPERADOR
        Profile.objects.create(user=instance, role=role)
    else:
        # Mantém o profile existente; cria se por algum motivo faltar.
        Profile.objects.get_or_create(user=instance)
