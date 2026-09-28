from django.db import models

from apps.usuarios.models import Usuario


class LogAuditoria(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING,
        db_column="usuario_id",
        null=True,
        blank=True,
        related_name="logs",
    )
    accion = models.CharField(max_length=60)
    entidad = models.CharField(max_length=60)
    entidad_id = models.CharField(max_length=60)
    detalle = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "logs_auditoria"
        ordering = ["-created_at"]
        verbose_name = "log de auditoria"
        verbose_name_plural = "logs de auditoria"

    def __str__(self):
        return f"{self.accion} {self.entidad}:{self.entidad_id}"
