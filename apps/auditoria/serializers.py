from rest_framework import serializers

from .models import LogAuditoria


class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.nombre", read_only=True)

    class Meta:
        model = LogAuditoria
        fields = [
            "id",
            "usuario",
            "usuario_nombre",
            "accion",
            "entidad",
            "entidad_id",
            "detalle",
            "created_at",
        ]
        read_only_fields = fields
