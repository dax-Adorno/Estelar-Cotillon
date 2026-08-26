"""Throttles personalizados de la API."""

from rest_framework.throttling import AnonRateThrottle


class PedidoPublicoAnonRateThrottle(AnonRateThrottle):
    """Limita la creacion anonima de pedidos publicos."""

    scope = "pedidos_publicos"


class RegistroAnonRateThrottle(AnonRateThrottle):
    """Limita intentos anonimos de registro."""

    scope = "registro"


class InicioSesionAnonRateThrottle(AnonRateThrottle):
    """Reduce ataques de fuerza bruta sobre el login."""

    scope = "inicio_sesion"
