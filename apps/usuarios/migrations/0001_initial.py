import uuid
from pathlib import Path

from django.conf import settings
from django.db import migrations, models

RUTA_SCHEMA = Path(settings.BASE_DIR).parent / "schema.sql"


def aplicar_schema_base(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('public.usuarios')")
        if cursor.fetchone()[0] is not None:
            return
        cursor.execute(RUTA_SCHEMA.read_text(encoding="utf-8"))


def revertir_schema_base(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            DROP VIEW IF EXISTS vw_consumo_insumos, vw_insumos_stock_bajo,
                                vw_productos_mas_vendidos, vw_ventas_diarias CASCADE;
            DROP TABLE IF EXISTS logs_auditoria, pagos, detalle_compra, compras, proveedores,
                                 alertas_inventario, movimientos_inventario, detalle_pedido,
                                 pedidos, receta_producto, insumos, productos, categorias,
                                 mesas, usuarios CASCADE;
            DROP FUNCTION IF EXISTS set_updated_at() CASCADE;
            DROP TYPE IF EXISTS estado_pago, metodo_pago, estado_compra, motivo_movimiento,
                                tipo_movimiento, estado_item_pedido, estado_pedido,
                                estado_mesa, rol_usuario CASCADE;
            """
        )


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(aplicar_schema_base, revertir_schema_base),
        migrations.CreateModel(
            name="Usuario",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=150, unique=True)),
                ("password", models.CharField(db_column="password_hash", max_length=255)),
                (
                    "rol",
                    models.CharField(
                        choices=[
                            ("mesero", "Mesero"),
                            ("cocina", "Cocina"),
                            ("admin", "Administrador"),
                            ("inventario", "Inventario"),
                        ],
                        default="mesero",
                        max_length=20,
                    ),
                ),
                ("activo", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "usuario",
                "verbose_name_plural": "usuarios",
                "db_table": "usuarios",
                "ordering": ["nombre"],
                "managed": False,
            },
        ),
    ]
