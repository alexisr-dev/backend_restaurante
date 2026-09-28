from django.db import models

from apps.productos.models import Insumo
from apps.usuarios.models import Usuario


class EstadoCompra(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    RECIBIDA = "recibida", "Recibida"
    CANCELADA = "cancelada", "Cancelada"


class Proveedor(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    contacto = models.CharField(max_length=120, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    id = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.DO_NOTHING, db_column="proveedor_id", related_name="compras"
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.DO_NOTHING, db_column="usuario_id", related_name="compras"
    )
    estado = models.CharField(max_length=20, choices=EstadoCompra.choices, default=EstadoCompra.PENDIENTE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "compras"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Compra #{self.id} - {self.estado}"

    def recalcular_total(self):
        agregado = self.detalles.aggregate(total=models.Sum("subtotal"))["total"] or 0
        self.total = agregado
        self.save(update_fields=["total"])
        return self.total


class DetalleCompra(models.Model):
    id = models.AutoField(primary_key=True)
    compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, db_column="compra_id", related_name="detalles"
    )
    insumo = models.ForeignKey(
        Insumo, on_delete=models.DO_NOTHING, db_column="insumo_id", related_name="compras"
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.GeneratedField(
        expression=models.F("cantidad") * models.F("precio_unitario"),
        output_field=models.DecimalField(max_digits=10, decimal_places=2),
        db_persist=True,
    )

    class Meta:
        managed = False
        db_table = "detalle_compra"
        verbose_name = "linea de compra"
        verbose_name_plural = "detalle de compra"

    def __str__(self):
        return f"{self.insumo_id} x {self.cantidad}"
