from rest_framework import mixins, viewsets

from apps.usuarios.permissions import GestionUsuarios

from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer


class LogAuditoriaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LogAuditoria.objects.select_related("usuario")
    serializer_class = LogAuditoriaSerializer
    permission_classes = [GestionUsuarios]
    filterset_fields = ["accion", "entidad", "usuario"]
    search_fields = ["entidad", "entidad_id"]
    ordering_fields = ["created_at"]
