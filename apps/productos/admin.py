from django.contrib import admin

from .models import Categoria, Insumo, Producto, RecetaProducto


class RecetaInline(admin.TabularInline):
    model = RecetaProducto
    extra = 1
    autocomplete_fields = ["insumo"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "descripcion"]
    search_fields = ["nombre"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "categoria", "precio", "activo"]
    list_filter = ["categoria", "activo"]
    search_fields = ["nombre"]
    inlines = [RecetaInline]


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "unidad_medida", "stock_actual", "stock_minimo", "costo_unitario", "activo"]
    list_filter = ["activo", "unidad_medida"]
    search_fields = ["nombre"]
    readonly_fields = ["stock_actual"]
