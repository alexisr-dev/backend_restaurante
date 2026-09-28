from rest_framework.permissions import SAFE_METHODS, BasePermission


class RolPermission(BasePermission):
    roles_lectura: tuple[str, ...] = ()
    roles_escritura: tuple[str, ...] = ()

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            return False
        if usuario.rol == "admin":
            return True
        permitidos = self.roles_lectura if request.method in SAFE_METHODS else self.roles_escritura
        return usuario.rol in permitidos


class GestionCatalogo(RolPermission):
    roles_lectura = ("mesero", "cocina", "inventario")
    roles_escritura = ("inventario",)


class GestionInventario(RolPermission):
    roles_lectura = ("cocina", "inventario")
    roles_escritura = ("inventario",)


class GestionProveedores(RolPermission):
    roles_lectura = ("inventario",)
    roles_escritura = ("inventario",)


class LecturaReportes(RolPermission):
    roles_lectura = ("inventario",)
    roles_escritura = ()
