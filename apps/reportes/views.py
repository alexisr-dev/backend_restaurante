from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import LecturaReportes

from . import queries, serializers


def _entero(request, nombre: str, defecto: int, maximo: int) -> int:
    try:
        valor = int(request.query_params.get(nombre, defecto))
    except (TypeError, ValueError):
        return defecto
    return max(1, min(valor, maximo))


class ReporteBaseView(APIView):
    permission_classes = [LecturaReportes]


class ResumenView(ReporteBaseView):
    def get(self, request):
        return Response(serializers.ResumenSerializer(queries.resumen_general()).data)


class VentasDiariasView(ReporteBaseView):
    def get(self, request):
        dias = _entero(request, "dias", 30, 365)
        datos = queries.ventas_diarias(dias)
        return Response(serializers.VentaDiariaSerializer(datos, many=True).data)


class ProductosMasVendidosView(ReporteBaseView):
    def get(self, request):
        limite = _entero(request, "limite", 10, 100)
        datos = queries.productos_mas_vendidos(limite)
        return Response(serializers.ProductoVendidoSerializer(datos, many=True).data)


class InsumosStockBajoView(ReporteBaseView):
    def get(self, request):
        datos = queries.insumos_stock_bajo()
        return Response(serializers.InsumoStockBajoSerializer(datos, many=True).data)


class ConsumoInsumosView(ReporteBaseView):
    def get(self, request):
        limite = _entero(request, "limite", 10, 100)
        datos = queries.consumo_insumos(limite)
        return Response(serializers.ConsumoInsumoSerializer(datos, many=True).data)


class VentasPorCategoriaView(ReporteBaseView):
    def get(self, request):
        dias = _entero(request, "dias", 30, 365)
        datos = queries.ventas_por_categoria(dias)
        return Response(serializers.VentaCategoriaSerializer(datos, many=True).data)


class HistorialPedidosView(ReporteBaseView):
    def get(self, request):
        limite = _entero(request, "limite", 25, 200)
        offset = max(0, int(request.query_params.get("offset", 0) or 0))
        estado = request.query_params.get("estado") or None
        datos = queries.historial_pedidos(limite, offset, estado)
        return Response(serializers.HistorialPedidoSerializer(datos, many=True).data)
