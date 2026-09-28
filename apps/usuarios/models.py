import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class RolUsuario(models.TextChoices):
    MESERO = "mesero", "Mesero"
    COCINA = "cocina", "Cocina"
    ADMIN = "admin", "Administrador"
    INVENTARIO = "inventario", "Inventario"


class UsuarioManager(BaseUserManager):
    use_in_migrations = False

    def _crear(self, email, nombre, rol, password, **extra):
        if not email:
            raise ValueError("El email es obligatorio.")
        usuario = self.model(email=self.normalize_email(email), nombre=nombre, rol=rol, **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, nombre="", rol=RolUsuario.MESERO, password=None, **extra):
        return self._crear(email, nombre, rol, password, **extra)

    def create_superuser(self, email, nombre="", rol=RolUsuario.ADMIN, password=None, **extra):
        extra.setdefault("activo", True)
        return self._crear(email, nombre, RolUsuario.ADMIN, password, **extra)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class Usuario(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=120)
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=255, db_column="password_hash")
    rol = models.CharField(max_length=20, choices=RolUsuario.choices, default=RolUsuario.MESERO)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_login = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    objects = UsuarioManager()

    class Meta:
        managed = False
        db_table = "usuarios"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

    @property
    def is_active(self):
        return self.activo

    @is_active.setter
    def is_active(self, valor):
        self.activo = valor

    @property
    def es_admin(self):
        return self.rol == RolUsuario.ADMIN

    @property
    def is_staff(self):
        return self.es_admin

    @property
    def is_superuser(self):
        return self.es_admin

    def has_perm(self, perm, obj=None):
        return self.es_admin

    def has_perms(self, perm_list, obj=None):
        return self.es_admin

    def has_module_perms(self, app_label):
        return self.es_admin
