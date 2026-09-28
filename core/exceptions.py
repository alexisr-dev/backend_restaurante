import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class ReglaNegocioError(Exception):
    def __init__(self, mensaje: str, codigo: str = "regla_negocio"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(mensaje)


def api_exception_handler(exc, context):
    if isinstance(exc, ReglaNegocioError):
        return Response(
            {"detail": exc.mensaje, "code": exc.codigo},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, IntegrityError):
        logger.warning("Integridad violada: %s", exc)
        return Response(
            {"detail": "La operacion viola una restriccion de integridad.", "code": "integridad"},
            status=status.HTTP_409_CONFLICT,
        )

    respuesta = exception_handler(exc, context)
    if respuesta is None:
        logger.exception("Error no controlado en %s", context.get("view"))
        return Response(
            {"detail": "Error interno del servidor.", "code": "error_interno"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(respuesta.data, dict) and "detail" not in respuesta.data:
        respuesta.data = {"detail": "Datos invalidos.", "code": "validacion", "errors": respuesta.data}
    return respuesta
