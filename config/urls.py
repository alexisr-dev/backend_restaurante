from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthcheck(_request):
    return JsonResponse({"status": "ok", "service": "backend_restaurante"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck),
    path("api/auth/", include("apps.usuarios.urls_auth")),
    path("api/usuarios/", include("apps.usuarios.urls")),
    path("api/catalogo/", include("apps.productos.urls")),
    path("api/inventario/", include("apps.inventario.urls")),
    path("api/proveedores/", include("apps.proveedores.urls")),
    path("api/reportes/", include("apps.reportes.urls")),
    path("api/auditoria/", include("apps.auditoria.urls")),
]
