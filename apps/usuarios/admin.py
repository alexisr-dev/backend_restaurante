from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ["nombre", "email", "rol", "activo", "created_at"]
    list_filter = ["rol", "activo"]
    search_fields = ["nombre", "email"]
    ordering = ["nombre"]
    filter_horizontal = ()
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("nombre", "rol", "activo")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nombre", "rol", "activo", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ["created_at", "updated_at"]
