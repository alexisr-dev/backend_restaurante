from django.contrib import admin

from .models import AlertaInventario, MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ["created_at", "insumo", "tipo", "motivo", "cantidad", "referencia", "usuario"]
    list_filter = ["tipo", "motivo"]
    search_fields = ["insumo__nombre", "referencia"]
    date_hierarchy = "created_at"


@admin.register(AlertaInventario)
class AlertaInventarioAdmin(admin.ModelAdmin):
    list_display = ["created_at", "insumo", "mensaje", "atendida"]
    list_filter = ["atendida"]
    search_fields = ["insumo__nombre"]
