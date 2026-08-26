"""Configuracion administrativa de clientes."""

from django.contrib import admin

from apps.clientes.models import Cliente, PerfilUsuario


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Gestion basica de clientes desde el respaldo tecnico."""

    list_display = ("nombre", "apellido", "email", "tipo_cliente", "activo")
    list_filter = ("tipo_cliente", "activo")
    search_fields = ("nombre", "apellido", "email", "razon_social", "cuit")


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Gestion de roles y aprobaciones mayoristas."""

    list_display = ("usuario", "rol", "mayorista_aprobado", "cliente")
    list_filter = ("rol", "mayorista_aprobado")
    search_fields = ("usuario__username", "usuario__email", "cliente__nombre")
