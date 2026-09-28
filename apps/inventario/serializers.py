from rest_framework import serializers

from .models import AlertaInventario, MotivoMovimiento, MovimientoInventario, TipoMovimiento


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source="insumo.nombre", read_only=True)
    unidad_medida = serializers.CharField(source="insumo.unidad_medida", read_only=True)
    usuario_nombre = serializers.CharField(source="usuario.nombre", read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = [
            "id",
            "insumo",
            "insumo_nombre",
            "unidad_medida",
            "tipo",
            "motivo",
            "cantidad",
            "referencia",
            "usuario",
            "usuario_nombre",
            "created_at",
        ]
        read_only_fields = fields


class RegistrarMovimientoSerializer(serializers.Serializer):
    insumo = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=TipoMovimiento.choices)
    motivo = serializers.ChoiceField(choices=MotivoMovimiento.choices)
    cantidad = serializers.DecimalField(max_digits=12, decimal_places=3, required=False)
    stock_objetivo = serializers.DecimalField(max_digits=12, decimal_places=3, required=False)
    referencia = serializers.CharField(max_length=60, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["tipo"] == TipoMovimiento.AJUSTE:
            if attrs.get("stock_objetivo") is None:
                raise serializers.ValidationError({"stock_objetivo": "Requerido para un ajuste."})
        elif not attrs.get("cantidad"):
            raise serializers.ValidationError({"cantidad": "Requerida para entradas y salidas."})
        return attrs


class AlertaInventarioSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source="insumo.nombre", read_only=True)
    stock_actual = serializers.DecimalField(
        source="insumo.stock_actual", max_digits=12, decimal_places=3, read_only=True
    )
    stock_minimo = serializers.DecimalField(
        source="insumo.stock_minimo", max_digits=12, decimal_places=3, read_only=True
    )

    class Meta:
        model = AlertaInventario
        fields = [
            "id",
            "insumo",
            "insumo_nombre",
            "stock_actual",
            "stock_minimo",
            "mensaje",
            "atendida",
            "created_at",
        ]
        read_only_fields = ["id", "insumo", "mensaje", "created_at"]
