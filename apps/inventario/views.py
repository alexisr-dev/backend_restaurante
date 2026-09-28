from decimal import Decimal

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import GestionInventario

from .models import AlertaInventario, MovimientoInventario
from .serializers import (
    AlertaInventarioSerializer,
    MovimientoInventarioSerializer,
    RegistrarMovimientoSerializer,
)
from .services import registrar_movimiento


class MovimientoInventarioViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = MovimientoInventario.objects.select_related("insumo", "usuario")
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [GestionInventario]
    filterset_fields = ["insumo", "tipo", "motivo"]
    search_fields = ["referencia", "insumo__nombre"]
    ordering_fields = ["created_at", "cantidad"]

    def create(self, request, *args, **kwargs):
        entrada = RegistrarMovimientoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        movimiento = registrar_movimiento(
            insumo_id=datos["insumo"],
            tipo=datos["tipo"],
            motivo=datos["motivo"],
            cantidad=datos.get("cantidad") or Decimal("0"),
            stock_objetivo=datos.get("stock_objetivo"),
            usuario=request.user,
            referencia=datos.get("referencia") or None,
        )
        return Response(MovimientoInventarioSerializer(movimiento).data, status=201)


class AlertaInventarioViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = AlertaInventario.objects.select_related("insumo")
    serializer_class = AlertaInventarioSerializer
    permission_classes = [GestionInventario]
    filterset_fields = ["atendida", "insumo"]
    ordering_fields = ["created_at"]

    @action(detail=True, methods=["post"])
    def atender(self, request, pk=None):
        alerta = self.get_object()
        alerta.atendida = True
        alerta.save(update_fields=["atendida"])
        return Response(AlertaInventarioSerializer(alerta).data)

    @action(detail=False, methods=["get"])
    def pendientes(self, request):
        pendientes = self.get_queryset().filter(atendida=False)
        return Response(AlertaInventarioSerializer(pendientes, many=True).data)
