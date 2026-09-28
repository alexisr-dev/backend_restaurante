from django.contrib import admin

from .models import Compra, DetalleCompra, Proveedor


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    readonly_fields = ["subtotal"]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ["nombre", "contacto", "telefono", "email", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre", "contacto", "email"]


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ["id", "proveedor", "usuario", "estado", "total", "created_at"]
    list_filter = ["estado", "proveedor"]
    date_hierarchy = "created_at"
    inlines = [DetalleCompraInline]
    readonly_fields = ["total"]
