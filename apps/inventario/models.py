from django.db import models

from apps.productos.models import Insumo
from apps.usuarios.models import Usuario


class TipoMovimiento(models.TextChoices):
    ENTRADA = "entrada", "Entrada"
    SALIDA = "salida", "Salida"
    AJUSTE = "ajuste", "Ajuste"


class MotivoMovimiento(models.TextChoices):
    VENTA = "venta", "Venta"
    COMPRA = "compra", "Compra"
    AJUSTE_MANUAL = "ajuste_manual", "Ajuste manual"
    MERMA = "merma", "Merma"


class MovimientoInventario(models.Model):
    id = models.BigAutoField(primary_key=True)
    insumo = models.ForeignKey(
        Insumo, on_delete=models.DO_NOTHING, db_column="insumo_id", related_name="movimientos"
    )
    tipo = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    motivo = models.CharField(max_length=20, choices=MotivoMovimiento.choices)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    referencia = models.CharField(max_length=60, blank=True, null=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING,
        db_column="usuario_id",
        null=True,
        blank=True,
        related_name="movimientos",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "movimientos_inventario"
        ordering = ["-created_at"]
        verbose_name = "movimiento de inventario"
        verbose_name_plural = "movimientos de inventario"

    def __str__(self):
        return f"{self.tipo} {self.cantidad} de insumo {self.insumo_id}"


class AlertaInventario(models.Model):
    id = models.BigAutoField(primary_key=True)
    insumo = models.ForeignKey(
        Insumo, on_delete=models.DO_NOTHING, db_column="insumo_id", related_name="alertas"
    )
    mensaje = models.TextField()
    atendida = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "alertas_inventario"
        ordering = ["-created_at"]
        verbose_name = "alerta de inventario"
        verbose_name_plural = "alertas de inventario"

    def __str__(self):
        return self.mensaje
