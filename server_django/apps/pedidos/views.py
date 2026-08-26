"""Vistas API de pedidos."""

# pylint: disable=too-many-ancestors

from rest_framework import permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.throttles import PedidoPublicoAnonRateThrottle
from apps.clientes.permissions import EsClienteEstelart, EsOperadorOAdmin

from apps.pedidos.models import DetallePedido, Pedido
from apps.pedidos.serializers import (
    DetallePedidoSerializer,
    PedidoPublicoCreateSerializer,
    PedidoPublicoResponseSerializer,
    PedidoClienteSerializer,
    PedidoSerializer,
)


class PedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de solo lectura para pedidos."""

    permission_classes = (EsOperadorOAdmin,)
    serializer_class = PedidoSerializer
    queryset = (
        Pedido.objects.select_related("cliente")
        .prefetch_related("detalles__producto")
        .all()
    )


class DetallePedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de solo lectura para detalles de pedidos."""

    permission_classes = (EsOperadorOAdmin,)
    serializer_class = DetallePedidoSerializer
    queryset = DetallePedido.objects.select_related(
        "pedido",
        "producto",
    ).all()


class PaginacionPedidosCliente(PageNumberPagination):
    """Paginacion acotada para historiales extensos."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class MisPedidosViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial aislado al cliente autenticado actual."""

    permission_classes = (EsClienteEstelart,)
    serializer_class = PedidoClienteSerializer
    pagination_class = PaginacionPedidosCliente

    def get_queryset(self):
        perfil = getattr(self.request.user, "perfil_estelart", None)
        if perfil is None or perfil.cliente_id is None:
            return Pedido.objects.none()
        return (
            Pedido.objects.filter(cliente_id=perfil.cliente_id)
            .prefetch_related("detalles__producto")
            .order_by("-creado_en")
        )


class PedidoPublicoCreateAPIView(APIView):
    """Endpoint publico para crear pedidos desde el frontend."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (PedidoPublicoAnonRateThrottle,)

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
