from decimal import Decimal

from apps.productos.models import Categoria, Insumo, Producto, RecetaProducto
from apps.usuarios.models import RolUsuario, Usuario

PASSWORD = "ClaveSegura2026!"


def crear_usuario(rol=RolUsuario.ADMIN, email=None, **extra):
    email = email or f"{rol}@test.com"
    return Usuario.objects.create_user(
        email=email, nombre=f"Usuario {rol}", rol=rol, password=PASSWORD, **extra
    )


def autenticar(cliente, usuario):
    respuesta = cliente.post(
        "/api/auth/login/",
        {"email": usuario.email, "password": PASSWORD},
        content_type="application/json",
    )
    token = respuesta.json()["access"]
    cliente.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return token


def crear_insumo(nombre="Insumo", stock="10.000", minimo="2.000"):
    return Insumo.objects.create(
        nombre=nombre,
        unidad_medida="kg",
        stock_actual=Decimal(stock),
        stock_minimo=Decimal(minimo),
        costo_unitario=Decimal("5.00"),
    )


def crear_producto_con_receta(nombre="Plato", precio="20.00", insumos=None):
    categoria, _ = Categoria.objects.get_or_create(nombre="Fondos")
    producto = Producto.objects.create(categoria=categoria, nombre=nombre, precio=Decimal(precio))
    for insumo, cantidad in (insumos or {}).items():
        RecetaProducto.objects.create(
            producto=producto, insumo=insumo, cantidad_requerida=Decimal(cantidad)
        )
    return producto
