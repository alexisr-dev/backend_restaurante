from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.productos.models import Insumo


@receiver(post_save, sender=Insumo, dispatch_uid="inventario_evaluar_alerta_stock")
def evaluar_alerta_stock(sender, instance, **kwargs):
    from .services import evaluar_alerta

    if instance.activo:
        evaluar_alerta(instance)
