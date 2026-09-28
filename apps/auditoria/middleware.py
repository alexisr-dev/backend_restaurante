import logging
import uuid

logger = logging.getLogger("auditoria")

METODOS_AUDITADOS = {"POST", "PUT", "PATCH", "DELETE"}
RUTAS_IGNORADAS = ("/api/auth/login/", "/api/auth/refresh/", "/api/auth/password/")

ACCION_POR_METODO = {
    "POST": "CREATE",
    "PUT": "UPDATE",
    "PATCH": "UPDATE",
    "DELETE": "DELETE",
}


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        respuesta = self.get_response(request)
        respuesta["X-Request-ID"] = request.request_id
        return respuesta


class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        respuesta = self.get_response(request)

        if not self._debe_auditar(request, respuesta):
            return respuesta

        from .models import LogAuditoria

        entidad, entidad_id = self._extraer_entidad(request.path)
        try:
            LogAuditoria.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                accion=ACCION_POR_METODO.get(request.method, request.method),
                entidad=entidad,
                entidad_id=entidad_id,
                detalle={
                    "path": request.path,
                    "method": request.method,
                    "status": respuesta.status_code,
                    "request_id": getattr(request, "request_id", None),
                },
            )
        except Exception:
            logger.exception("No se pudo registrar el log de auditoria")

        return respuesta

    @staticmethod
    def _debe_auditar(request, respuesta) -> bool:
        if request.method not in METODOS_AUDITADOS:
            return False
        if not request.path.startswith("/api/"):
            return False
        if request.path in RUTAS_IGNORADAS:
            return False
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return False
        return 200 <= respuesta.status_code < 400

    @staticmethod
    def _extraer_entidad(path: str) -> tuple[str, str]:
        partes = [p for p in path.split("/") if p and p not in ("api", "v1")]
        if not partes:
            return "desconocido", "-"
        if len(partes) >= 3:
            return partes[1], partes[2]
        if len(partes) == 2:
            return partes[1], "-"
        return partes[0], "-"
