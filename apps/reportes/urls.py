from django.urls import path

from .views import (
    ConsumoInsumosView,
    HistorialPedidosView,
    InsumosStockBajoView,
    ProductosMasVendidosView,
    ResumenView,
    VentasDiariasView,
    VentasPorCategoriaView,
)

urlpatterns = [
    path("resumen/", ResumenView.as_view(), name="reporte-resumen"),
    path("ventas-diarias/", VentasDiariasView.as_view(), name="reporte-ventas-diarias"),
    path("productos-mas-vendidos/", ProductosMasVendidosView.as_view(), name="reporte-top-productos"),
    path("insumos-stock-bajo/", InsumosStockBajoView.as_view(), name="reporte-stock-bajo"),
    path("consumo-insumos/", ConsumoInsumosView.as_view(), name="reporte-consumo"),
    path("ventas-por-categoria/", VentasPorCategoriaView.as_view(), name="reporte-categorias"),
    path("pedidos/", HistorialPedidosView.as_view(), name="reporte-historial-pedidos"),
]
