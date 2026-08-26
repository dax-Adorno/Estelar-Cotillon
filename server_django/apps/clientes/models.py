"""Modelos de clientes."""

# pylint: disable=too-many-ancestors

from django.conf import settings
from django.db import models


class Cliente(models.Model):
    """Cliente minorista o mayorista de ESTELART."""

    class TipoCliente(models.TextChoices):
        """Tipos comerciales de cliente."""

        MINORISTA = "minorista", "Minorista"
        MAYORISTA = "mayorista", "Mayorista"

    nombre = models.CharField(max_length=160)
    apellido = models.CharField(max_length=160, blank=True)
    razon_social = models.CharField(max_length=180, blank=True)
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TipoCliente.choices,
        default=TipoCliente.MINORISTA,
    )
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=40, blank=True)
    whatsapp = models.CharField(max_length=40, blank=True)
    documento = models.CharField(max_length=40, blank=True)
    cuit = models.CharField(max_length=40, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=120, blank=True)
    provincia = models.CharField(max_length=120, blank=True)
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clientes"
        ordering = ["nombre", "apellido"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        indexes = [
            models.Index(fields=["tipo_cliente"]),
            models.Index(fields=["activo"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        if self.razon_social:
            return self.razon_social

        nombre_completo = f"{self.nombre} {self.apellido}".strip()
        return nombre_completo


class PerfilUsuario(models.Model):
    """Rol comercial y operativo asociado a una cuenta autenticada."""

    class Rol(models.TextChoices):
        """Roles disponibles en la plataforma."""

        CLIENTE_MINORISTA = "cliente_minorista", "Cliente minorista"
        CLIENTE_MAYORISTA = "cliente_mayorista", "Cliente mayorista"
        OPERADOR = "operador", "Operador"
        ADMIN = "admin", "Administrador"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_estelart",
    )
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.SET_NULL,
        related_name="perfil_usuario",
        null=True,
        blank=True,
    )
    rol = models.CharField(
        max_length=30,
        choices=Rol.choices,
        default=Rol.CLIENTE_MINORISTA,
    )
    mayorista_aprobado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "perfiles_usuario"
        verbose_name = "perfil de usuario"
        verbose_name_plural = "perfiles de usuario"
        indexes = [models.Index(fields=["rol"])]

    def __str__(self) -> str:
        return f"{self.usuario.username} ({self.get_rol_display()})"
