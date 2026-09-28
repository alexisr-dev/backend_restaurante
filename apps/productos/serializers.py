from rest_framework import serializers

from .models import Categoria, Insumo, Producto, RecetaProducto


class CategoriaSerializer(serializers.ModelSerializer):
    total_productos = serializers.IntegerField(read_only=True)

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "total_productos"]


class InsumoSerializer(serializers.ModelSerializer):
    en_alerta = serializers.BooleanField(read_only=True)

    class Meta:
        model = Insumo
        fields = [
            "id",
            "nombre",
            "unidad_medida",
            "stock_actual",
            "stock_minimo",
            "costo_unitario",
            "activo",
            "en_alerta",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "stock_actual", "created_at", "updated_at"]


class RecetaProductoSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source="insumo.nombre", read_only=True)
    unidad_medida = serializers.CharField(source="insumo.unidad_medida", read_only=True)

    class Meta:
        model = RecetaProducto
        fields = ["id", "producto", "insumo", "insumo_nombre", "unidad_medida", "cantidad_requerida"]

    def validate_cantidad_requerida(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("Debe ser mayor que cero.")
        return valor


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    receta = RecetaProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "categoria",
            "categoria_nombre",
            "nombre",
            "descripcion",
            "precio",
            "activo",
            "receta",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_precio(self, valor):
        if valor < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return valor
