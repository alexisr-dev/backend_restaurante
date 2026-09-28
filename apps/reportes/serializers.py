from rest_framework import serializers


class VentaDiariaSerializer(serializers.Serializer):
    dia = serializers.DateTimeField()
    num_pedidos = serializers.IntegerField()
    total_vendido = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProductoVendidoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    unidades_vendidas = serializers.IntegerField()
    ingresos = serializers.DecimalField(max_digits=12, decimal_places=2)


class InsumoStockBajoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    stock_actual = serializers.DecimalField(max_digits=12, decimal_places=3)
    stock_minimo = serializers.DecimalField(max_digits=12, decimal_places=3)


class ConsumoInsumoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    total_consumido = serializers.DecimalField(max_digits=14, decimal_places=3)


class VentaCategoriaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    ingresos = serializers.DecimalField(max_digits=12, decimal_places=2)
    unidades = serializers.IntegerField()


class ResumenSerializer(serializers.Serializer):
    ventas_hoy = serializers.DecimalField(max_digits=12, decimal_places=2)
    pedidos_hoy = serializers.IntegerField()
    pedidos_activos = serializers.IntegerField()
    mesas_ocupadas = serializers.IntegerField()
    mesas_totales = serializers.IntegerField()
    insumos_en_alerta = serializers.IntegerField()
    alertas_pendientes = serializers.IntegerField()
    productos_activos = serializers.IntegerField()


class HistorialPedidoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    estado = serializers.CharField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()
    mesa_numero = serializers.IntegerField()
    mesero_nombre = serializers.CharField()
    lineas = serializers.IntegerField()
