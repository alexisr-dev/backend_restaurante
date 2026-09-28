from decimal import Decimal

from django.db import transaction

from apps.productos.models import Insumo
from core.exceptions import ReglaNegocioError

from .models import AlertaInventario, MotivoMovimiento, MovimientoInventario, TipoMovimiento

DELTA_POR_TIPO = {
    TipoMovimiento.ENTRADA: Decimal("1"),
    TipoMovimiento.SALIDA: Decimal("-1"),
}


def evaluar_alerta(insumo: Insumo) -> AlertaInventario | None:
    if insumo.stock_actual > insumo.stock_minimo:
        AlertaInventario.objects.filter(insumo=insumo, atendida=False).update(atendida=True)
        return None

    if AlertaInventario.objects.filter(insumo=insumo, atendida=False).exists():
        return None

    return AlertaInventario.objects.create(
        insumo=insumo,
        mensaje=(
            f"Stock bajo de '{insumo.nombre}': {insumo.stock_actual} {insumo.unidad_medida} "
            f"(minimo {insumo.stock_minimo})."
        ),
    )


@transaction.atomic
def registrar_movimiento(
    *,
    insumo_id: int,
    tipo: str,
    motivo: str,
    cantidad: Decimal,
    usuario=None,
    referencia: str | None = None,
    stock_objetivo: Decimal | None = None,
) -> MovimientoInventario:
    if cantidad is not None and cantidad <= 0 and tipo != TipoMovimiento.AJUSTE:
        raise ReglaNegocioError("La cantidad debe ser mayor que cero.")

    insumo = Insumo.objects.select_for_update().filter(pk=insumo_id).first()
    if insumo is None:
        raise ReglaNegocioError("El insumo indicado no existe.", codigo="insumo_inexistente")

    if tipo == TipoMovimiento.AJUSTE:
        if stock_objetivo is None:
            raise ReglaNegocioError("Un ajuste requiere el stock objetivo.", codigo="ajuste_sin_objetivo")
        if stock_objetivo < 0:
            raise ReglaNegocioError("El stock objetivo no puede ser negativo.")
        cantidad = abs(stock_objetivo - insumo.stock_actual)
        insumo.stock_actual = stock_objetivo
    else:
        delta = DELTA_POR_TIPO[tipo] * cantidad
        nuevo_stock = insumo.stock_actual + delta
        if nuevo_stock < 0:
            raise ReglaNegocioError(
                f"Stock insuficiente de '{insumo.nombre}': disponible {insumo.stock_actual}, "
                f"solicitado {cantidad}.",
                codigo="stock_insuficiente",
            )
        insumo.stock_actual = nuevo_stock

    insumo.save(update_fields=["stock_actual"])

    movimiento = MovimientoInventario.objects.create(
        insumo=insumo,
        tipo=tipo,
        motivo=motivo,
        cantidad=cantidad if cantidad > 0 else Decimal("0.001"),
        referencia=referencia,
        usuario=usuario,
    )
    evaluar_alerta(insumo)
    return movimiento


@transaction.atomic
def recibir_compra(compra, usuario=None) -> None:
    for linea in compra.detalles.select_related("insumo"):
        registrar_movimiento(
            insumo_id=linea.insumo_id,
            tipo=TipoMovimiento.ENTRADA,
            motivo=MotivoMovimiento.COMPRA,
            cantidad=linea.cantidad,
            usuario=usuario,
            referencia=f"compra:{compra.id}",
        )
        insumo = linea.insumo
        insumo.costo_unitario = linea.precio_unitario
        insumo.save(update_fields=["costo_unitario"])
