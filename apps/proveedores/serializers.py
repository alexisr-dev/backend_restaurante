from rest_framework import serializers

from .models import Compra, DetalleCompra, EstadoCompra, Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["id", "nombre", "contacto", "telefono", "email", "direccion", "activo"]


class DetalleCompraSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source="insumo.nombre", read_only=True)
    unidad_medida = serializers.CharField(source="insumo.unidad_medida", read_only=True)

    class Meta:
        model = DetalleCompra
        fields = [
            "id",
            "insumo",
            "insumo_nombre",
            "unidad_medida",
            "cantidad",
            "precio_unitario",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal"]

    def validate_cantidad(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("Debe ser mayor que cero.")
        return valor


class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True)
    proveedor_nombre = serializers.CharField(source="proveedor.nombre", read_only=True)
    usuario_nombre = serializers.CharField(source="usuario.nombre", read_only=True)

    class Meta:
        model = Compra
        fields = [
            "id",
            "proveedor",
            "proveedor_nombre",
            "usuario",
            "usuario_nombre",
            "estado",
            "total",
            "detalles",
            "created_at",
        ]
        read_only_fields = ["id", "usuario", "estado", "total", "created_at"]

    def validate_detalles(self, valor):
        if not valor:
            raise serializers.ValidationError("La compra debe tener al menos una linea.")
        return valor

    def create(self, validated_data):
        lineas = validated_data.pop("detalles")
        compra = Compra.objects.create(
            usuario=self.context["request"].user,
            estado=EstadoCompra.PENDIENTE,
            **validated_data,
        )
        DetalleCompra.objects.bulk_create(
            [DetalleCompra(compra=compra, **linea) for linea in lineas]
        )
        compra.refresh_from_db()
        compra.recalcular_total()
        return compra
