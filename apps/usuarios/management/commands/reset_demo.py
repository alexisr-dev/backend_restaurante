from django.core.management.base import BaseCommand
from django.db import connection, transaction

TABLAS_OPERATIVAS = [
    "pagos",
    "detalle_pedido",
    "pedidos",
    "detalle_compra",
    "compras",
    "movimientos_inventario",
    "alertas_inventario",
    "logs_auditoria",
]


class Command(BaseCommand):
    help = "Vacia la operacion (pedidos, compras, movimientos) y deja el catalogo intacto."

    def add_arguments(self, parser):
        parser.add_argument(
            "--todo",
            action="store_true",
            help="Elimina tambien catalogo, insumos, proveedores y usuarios.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        tablas = list(TABLAS_OPERATIVAS)
        if options["todo"]:
            tablas += ["receta_producto", "productos", "categorias", "insumos", "proveedores", "mesas"]

        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE {', '.join(tablas)} RESTART IDENTITY CASCADE")
            if not options["todo"]:
                cursor.execute("UPDATE mesas SET estado = 'libre'")

        self.stdout.write(self.style.SUCCESS(f"Tablas vaciadas: {len(tablas)}"))
