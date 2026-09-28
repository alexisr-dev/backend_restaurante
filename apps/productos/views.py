from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import GestionCatalogo

from .models import Categoria, Insumo, Producto, RecetaProducto
from .serializers import (
    CategoriaSerializer,
    InsumoSerializer,
    ProductoSerializer,
    RecetaProductoSerializer,
)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.annotate(total_productos=Count("productos"))
    serializer_class = CategoriaSerializer
    permission_classes = [GestionCatalogo]
    search_fields = ["nombre"]
    ordering_fields = ["nombre"]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related("categoria").prefetch_related("receta__insumo")
    serializer_class = ProductoSerializer
    permission_classes = [GestionCatalogo]
    filterset_fields = ["categoria", "activo"]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "precio", "created_at"]

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])

    @action(detail=True, methods=["get", "post"], url_path="receta")
    def receta(self, request, pk=None):
        producto = self.get_object()
        if request.method == "GET":
            lineas = producto.receta.select_related("insumo")
            return Response(RecetaProductoSerializer(lineas, many=True).data)

        serializer = RecetaProductoSerializer(data={**request.data, "producto": producto.pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [GestionCatalogo]
    filterset_fields = ["activo", "unidad_medida"]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "stock_actual", "costo_unitario"]

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])


class RecetaProductoViewSet(viewsets.ModelViewSet):
    queryset = RecetaProducto.objects.select_related("insumo", "producto")
    serializer_class = RecetaProductoSerializer
    permission_classes = [GestionCatalogo]
    filterset_fields = ["producto", "insumo"]
