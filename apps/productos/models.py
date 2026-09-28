from django.db import models


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "categorias"
        ordering = ["nombre"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="categoria_id",
        related_name="productos",
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Insumo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120, unique=True)
    unidad_medida = models.CharField(max_length=20)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "insumos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.unidad_medida})"

    @property
    def en_alerta(self):
        return self.stock_actual <= self.stock_minimo


class RecetaProducto(models.Model):
    id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, db_column="producto_id", related_name="receta"
    )
    insumo = models.ForeignKey(
        Insumo, on_delete=models.RESTRICT, db_column="insumo_id", related_name="usos"
    )
    cantidad_requerida = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        managed = False
        db_table = "receta_producto"
        unique_together = [("producto", "insumo")]
        verbose_name = "linea de receta"
        verbose_name_plural = "recetas"

    def __str__(self):
        return f"{self.producto_id} -> {self.insumo_id} x{self.cantidad_requerida}"
