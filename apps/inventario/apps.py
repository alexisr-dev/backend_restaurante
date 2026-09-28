from django.apps import AppConfig


class InventarioConfig(AppConfig):
    name = "apps.inventario"
    label = "inventario"
    verbose_name = "Inventario y alertas"

    def ready(self):
        from . import signals  # noqa: F401
