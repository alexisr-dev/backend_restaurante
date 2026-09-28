from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.inventario.services import recibir_compra
from core.exceptions import ReglaNegocioError
from core.permissions import GestionProveedores

from .models import Compra, EstadoCompra, Proveedor
from .serializers import CompraSerializer, ProveedorSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [GestionProveedores]
    filterset_fields = ["activo"]
    search_fields = ["nombre", "contacto", "email"]
    ordering_fields = ["nombre"]

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.select_related("proveedor", "usuario").prefetch_related(
        "detalles__insumo"
    )
    serializer_class = CompraSerializer
    permission_classes = [GestionProveedores]
    filterset_fields = ["estado", "proveedor"]
    ordering_fields = ["created_at", "total"]
    http_method_names = ["get", "post", "head", "options"]

    @action(detail=True, methods=["post"])
    def recibir(self, request, pk=None):
        compra = self.get_object()
        if compra.estado != EstadoCompra.PENDIENTE:
            raise ReglaNegocioError(
                f"Solo se puede recibir una compra pendiente (estado actual: {compra.estado}).",
                codigo="estado_invalido",
            )

        with transaction.atomic():
            recibir_compra(compra, usuario=request.user)
            compra.estado = EstadoCompra.RECIBIDA
            compra.save(update_fields=["estado"])

        compra.refresh_from_db()
        return Response(CompraSerializer(compra).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        compra = self.get_object()
        if compra.estado != EstadoCompra.PENDIENTE:
            raise ReglaNegocioError(
                "Solo se puede cancelar una compra pendiente.", codigo="estado_invalido"
            )
        compra.estado = EstadoCompra.CANCELADA
        compra.save(update_fields=["estado"])
        return Response(CompraSerializer(compra).data)
