"""Permisos centralizados para roles de ESTELART."""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.clientes.models import PerfilUsuario


def obtener_rol_usuario(usuario: Any) -> str | None:
    """Resuelve rol de perfil y mantiene compatibilidad con staff de Django."""
    if not getattr(usuario, "is_authenticated", False):
        return None
    if getattr(usuario, "is_superuser", False):
        return PerfilUsuario.Rol.ADMIN

    perfil = getattr(usuario, "perfil_estelart", None)
    if perfil is not None:
        return perfil.rol
    if getattr(usuario, "is_staff", False):
        return PerfilUsuario.Rol.OPERADOR
    return PerfilUsuario.Rol.CLIENTE_MINORISTA


class EsOperadorOAdmin(BasePermission):
    """Permite acceso interno a operadores y administradores."""

    message = "No tienes permisos operativos para realizar esta accion."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return obtener_rol_usuario(request.user) in {
            PerfilUsuario.Rol.OPERADOR,
            PerfilUsuario.Rol.ADMIN,
        }


class EsAdminEstelart(BasePermission):
    """Restringe la gestion de roles a administradores."""

    message = "Solo un administrador puede gestionar roles y aprobaciones."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return obtener_rol_usuario(request.user) == PerfilUsuario.Rol.ADMIN


class EsMayoristaAprobado(BasePermission):
    """Comprueba rol mayorista y aprobacion comercial explicita."""

    message = "La cuenta mayorista todavia no fue aprobada."

    def has_permission(self, request: Request, view: APIView) -> bool:
        if obtener_rol_usuario(request.user) != PerfilUsuario.Rol.CLIENTE_MAYORISTA:
            return False
        perfil = getattr(request.user, "perfil_estelart", None)
        return bool(perfil and perfil.mayorista_aprobado)


class EsClienteEstelart(BasePermission):
    """Permite acceso a clientes autenticados con ficha comercial vinculada."""

    message = "La cuenta no tiene un perfil de cliente asociado."

    def has_permission(self, request: Request, view: APIView) -> bool:
        rol = obtener_rol_usuario(request.user)
        if rol not in {
            PerfilUsuario.Rol.CLIENTE_MINORISTA,
            PerfilUsuario.Rol.CLIENTE_MAYORISTA,
        }:
            return False
        perfil = getattr(request.user, "perfil_estelart", None)
        return bool(perfil and perfil.cliente_id)
