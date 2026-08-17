"""Vistas API de pedidos."""

# pylint: disable=too-many-ancestors

from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pedidos.models import DetallePedido, Pedido
from apps.pedidos.serializers import (
    DetallePedidoSerializer,
    PedidoPublicoCreateSerializer,
    PedidoPublicoResponseSerializer,
    PedidoSerializer,
)


class PedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de solo lectura para pedidos."""

    permission_classes = (permissions.IsAdminUser,)
    serializer_class = PedidoSerializer
    queryset = (
        Pedido.objects.select_related("cliente")
        .prefetch_related("detalles__producto")
        .all()
    )


class DetallePedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de solo lectura para detalles de pedidos."""

    permission_classes = (permissions.IsAdminUser,)
    serializer_class = DetallePedidoSerializer
    queryset = DetallePedido.objects.select_related(
        "pedido",
        "producto",
    ).all()


class PedidoPublicoCreateAPIView(APIView):
    """Endpoint publico para crear pedidos desde el frontend."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        """Crea un pedido a partir del carrito del frontend."""
        serializer = PedidoPublicoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pedido = serializer.save()
        response_serializer = PedidoPublicoResponseSerializer(
            pedido,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
