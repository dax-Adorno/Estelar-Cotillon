"""Vistas API de pedidos."""

# pylint: disable=too-many-ancestors

from rest_framework import permissions, viewsets

from apps.pedidos.models import DetallePedido, Pedido
from apps.pedidos.serializers import DetallePedidoSerializer, PedidoSerializer


class PedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para pedidos."""

    serializer_class = PedidoSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = Pedido.objects.select_related("cliente").prefetch_related(
        "detalles__producto",
    )


class DetallePedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para detalles de pedidos."""

    serializer_class = DetallePedidoSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = DetallePedido.objects.select_related(
        "pedido",
        "producto",
    )
