from django.contrib import admin

from .models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ["created_at", "usuario", "accion", "entidad", "entidad_id"]
    list_filter = ["accion", "entidad"]
    search_fields = ["entidad", "entidad_id"]
    date_hierarchy = "created_at"
    readonly_fields = ["usuario", "accion", "entidad", "entidad_id", "detalle", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
