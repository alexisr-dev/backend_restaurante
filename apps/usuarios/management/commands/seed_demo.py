from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.productos.models import Categoria, Insumo, Producto, RecetaProducto
from apps.proveedores.models import Proveedor
from apps.usuarios.models import RolUsuario, Usuario

USUARIOS = [
    ("Alexis Admin", "admin@restaurante.com", RolUsuario.ADMIN, "Admin2026!"),
    ("Lucia Mesera", "mesero@restaurante.com", RolUsuario.MESERO, "Mesero2026!"),
    ("Carlos Cocina", "cocina@restaurante.com", RolUsuario.COCINA, "Cocina2026!"),
    ("Rosa Almacen", "inventario@restaurante.com", RolUsuario.INVENTARIO, "Inventario2026!"),
]

CATEGORIAS = [
    ("Entradas", "Platos de inicio y piqueos"),
    ("Fondos", "Platos principales de la carta"),
    ("Bebidas", "Bebidas frias y calientes"),
    ("Postres", "Dulces y postres de la casa"),
]

INSUMOS = [
    ("Lomo de res", "kg", "18.000", "5.000", "38.00"),
    ("Cebolla roja", "kg", "12.000", "4.000", "4.50"),
    ("Tomate", "kg", "9.000", "3.000", "5.20"),
    ("Papa amarilla", "kg", "25.000", "8.000", "3.80"),
    ("Arroz", "kg", "40.000", "10.000", "4.20"),
    ("Pollo", "kg", "22.000", "6.000", "12.50"),
    ("Pescado bonito", "kg", "7.000", "4.000", "22.00"),
    ("Limon", "kg", "6.000", "3.000", "6.00"),
    ("Aji amarillo", "kg", "3.500", "2.000", "9.00"),
    ("Leche evaporada", "l", "14.000", "6.000", "5.10"),
    ("Harina", "kg", "16.000", "5.000", "3.60"),
    ("Azucar", "kg", "11.000", "4.000", "4.00"),
    ("Cafe molido", "kg", "2.500", "2.000", "48.00"),
    ("Gaseosa 500ml", "unidad", "60.000", "24.000", "2.50"),
    ("Aceite vegetal", "l", "10.000", "4.000", "8.90"),
]

PRODUCTOS = [
    ("Fondos", "Lomo Saltado", "Clasico salteado de lomo con papas y arroz", "34.00",
     [("Lomo de res", "0.250"), ("Cebolla roja", "0.100"), ("Tomate", "0.080"),
      ("Papa amarilla", "0.200"), ("Arroz", "0.150"), ("Aceite vegetal", "0.030")]),
    ("Fondos", "Arroz con Pollo", "Arroz verde con presa de pollo y salsa criolla", "28.00",
     [("Pollo", "0.300"), ("Arroz", "0.200"), ("Cebolla roja", "0.060"), ("Aceite vegetal", "0.025")]),
    ("Fondos", "Aji de Gallina", "Crema de aji amarillo con pollo deshilachado", "26.00",
     [("Pollo", "0.250"), ("Aji amarillo", "0.070"), ("Leche evaporada", "0.150"),
      ("Papa amarilla", "0.150"), ("Arroz", "0.120")]),
    ("Entradas", "Ceviche Clasico", "Pescado fresco en leche de tigre", "32.00",
     [("Pescado bonito", "0.220"), ("Limon", "0.150"), ("Cebolla roja", "0.080"),
      ("Aji amarillo", "0.030")]),
    ("Entradas", "Papa a la Huancaina", "Papa amarilla con crema huancaina", "18.00",
     [("Papa amarilla", "0.250"), ("Aji amarillo", "0.050"), ("Leche evaporada", "0.100")]),
    ("Entradas", "Causa Limena", "Causa rellena de pollo", "20.00",
     [("Papa amarilla", "0.300"), ("Pollo", "0.120"), ("Limon", "0.040"), ("Aji amarillo", "0.030")]),
    ("Bebidas", "Chicha Morada", "Jarra de chicha morada de la casa", "12.00",
     [("Azucar", "0.080"), ("Limon", "0.030")]),
    ("Bebidas", "Gaseosa Personal", "Botella personal 500ml", "6.00",
     [("Gaseosa 500ml", "1.000")]),
    ("Bebidas", "Cafe Pasado", "Taza de cafe de altura", "8.00",
     [("Cafe molido", "0.020"), ("Leche evaporada", "0.050")]),
    ("Postres", "Suspiro Limeno", "Manjar blanco con merengue al oporto", "14.00",
     [("Leche evaporada", "0.180"), ("Azucar", "0.090")]),
    ("Postres", "Picarones", "Buñuelos de zapallo con miel de chancaca", "13.00",
     [("Harina", "0.150"), ("Azucar", "0.080"), ("Aceite vegetal", "0.060")]),
]

PROVEEDORES = [
    ("Distribuidora Andina SAC", "Marco Ruiz", "987654321", "ventas@andina.pe", "Av. Argentina 1450, Lima"),
    ("Frigorifico El Sol", "Elena Paz", "987112233", "pedidos@elsol.pe", "Jr. Huallaga 320, Lima"),
    ("Mercado Mayorista Santa Anita", "Jose Quispe", "986554433", "contacto@mayorista.pe", "Santa Anita, Lima"),
]


class Command(BaseCommand):
    help = "Carga datos de demostracion coherentes para todo el sistema."

    def add_arguments(self, parser):
        parser.add_argument("--mesas", type=int, default=12, help="Cantidad de mesas a crear.")

    @transaction.atomic
    def handle(self, *args, **options):
        self._crear_usuarios()
        self._crear_mesas(options["mesas"])
        categorias = self._crear_categorias()
        insumos = self._crear_insumos()
        self._crear_productos(categorias, insumos)
        self._crear_proveedores()
        self.stdout.write(self.style.SUCCESS("Datos de demostracion cargados."))

    def _crear_usuarios(self):
        for nombre, email, rol, password in USUARIOS:
            usuario = Usuario.objects.filter(email=email).first()
            if usuario is None:
                Usuario.objects.create_user(email=email, nombre=nombre, rol=rol, password=password)
                self.stdout.write(f"  usuario creado: {email} / {password}")
            else:
                usuario.nombre = nombre
                usuario.rol = rol
                usuario.activo = True
                usuario.set_password(password)
                usuario.save()

    def _crear_mesas(self, cantidad):
        with connection.cursor() as cursor:
            for numero in range(1, cantidad + 1):
                capacidad = 2 if numero <= 3 else (6 if numero > 9 else 4)
                cursor.execute(
                    """
                    INSERT INTO mesas (numero, capacidad, estado)
                    VALUES (%s, %s, 'libre')
                    ON CONFLICT (numero) DO UPDATE SET capacidad = EXCLUDED.capacidad
                    """,
                    [numero, capacidad],
                )
        self.stdout.write(f"  mesas listas: {cantidad}")

    def _crear_categorias(self):
        creadas = {}
        for nombre, descripcion in CATEGORIAS:
            categoria, _ = Categoria.objects.get_or_create(
                nombre=nombre, defaults={"descripcion": descripcion}
            )
            creadas[nombre] = categoria
        return creadas

    def _crear_insumos(self):
        creados = {}
        for nombre, unidad, stock, minimo, costo in INSUMOS:
            insumo, _ = Insumo.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "unidad_medida": unidad,
                    "stock_actual": Decimal(stock),
                    "stock_minimo": Decimal(minimo),
                    "costo_unitario": Decimal(costo),
                },
            )
            creados[nombre] = insumo
        self.stdout.write(f"  insumos listos: {len(creados)}")
        return creados

    def _crear_productos(self, categorias, insumos):
        for categoria, nombre, descripcion, precio, receta in PRODUCTOS:
            producto, creado = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "categoria": categorias[categoria],
                    "descripcion": descripcion,
                    "precio": Decimal(precio),
                },
            )
            if not creado:
                continue
            RecetaProducto.objects.bulk_create(
                [
                    RecetaProducto(
                        producto=producto,
                        insumo=insumos[insumo_nombre],
                        cantidad_requerida=Decimal(cantidad),
                    )
                    for insumo_nombre, cantidad in receta
                ]
            )
        self.stdout.write(f"  productos listos: {Producto.objects.count()}")

    def _crear_proveedores(self):
        for nombre, contacto, telefono, email, direccion in PROVEEDORES:
            Proveedor.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "contacto": contacto,
                    "telefono": telefono,
                    "email": email,
                    "direccion": direccion,
                },
            )
        self.stdout.write(f"  proveedores listos: {Proveedor.objects.count()}")
