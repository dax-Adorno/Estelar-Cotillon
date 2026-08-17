"""Throttles personalizados de la API."""

from rest_framework.throttling import AnonRateThrottle


class PedidoPublicoAnonRateThrottle(AnonRateThrottle):
    """Limita la creacion anonima de pedidos publicos."""

    scope = "pedidos_publicos"
