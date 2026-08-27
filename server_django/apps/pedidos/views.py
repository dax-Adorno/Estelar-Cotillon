"""Vistas API de pedidos."""

# pylint: disable=too-many-ancestors

from django.db.models import Count, IntegerField, QuerySet, Sum, Value
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.throttles import PedidoPublicoAnonRateThrottle
from apps.clientes.permissions import EsClienteEstelart, EsOperadorOAdmin

from apps.pedidos.models import DetallePedido, Pedido
from apps.pedidos.serializers import (
    CambioEstadoPagoPedidoSerializer,
    CambioEstadoPedidoSerializer,
    DetallePedidoSerializer,
    PedidoClienteSerializer,
    PedidoPublicoCreateSerializer,
    PedidoPublicoResponseSerializer,
    PedidoResumenSerializer,
    PedidoSerializer,
)
from apps.pedidos.services import (
    TransicionPedidoError,
    cambiar_estado_pago_pedido,
    cambiar_estado_pedido,
)


class PaginacionPedidosInternos(PageNumberPagination):
    """Paginacion para listados operativos extensos."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class PedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta y transiciones controladas para personal interno."""

    permission_classes = (EsOperadorOAdmin,)
    pagination_class = PaginacionPedidosInternos
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = (
        "codigo",
        "cliente__nombre",
        "cliente__apellido",
        "cliente__razon_social",
        "cliente__email",
        "cliente__whatsapp",
    )
    ordering_fields = ("creado_en", "actualizado_en", "total", "codigo")
    ordering = ("-creado_en",)

    def get_serializer_class(self):
        if self.action == "list":
            return PedidoResumenSerializer
        if self.action == "cambiar_estado":
            return CambioEstadoPedidoSerializer
        if self.action == "cambiar_estado_pago":
            return CambioEstadoPagoPedidoSerializer
        return PedidoSerializer

    def get_queryset(self) -> QuerySet[Pedido]:
        queryset = Pedido.objects.select_related("cliente").annotate(
            cantidad_items=Count("detalles"),
            cantidad_unidades=Coalesce(
                Sum("detalles__cantidad"),
                Value(0),
                output_field=IntegerField(),
            ),
        )
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "detalles__producto",
                "eventos__usuario",
            )

        filtros_eleccion = {
            "estado": set(Pedido.EstadoPedido.values),
            "estado_pago": set(Pedido.EstadoPago.values),
            "canal_venta": set(Pedido.CanalVenta.values),
        }
        for campo, permitidos in filtros_eleccion.items():
            valor = self.request.query_params.get(campo)
            if valor is None:
                continue
            if valor not in permitidos:
                raise serializers.ValidationError(
                    {campo: "El valor indicado no es valido."},
                )
            queryset = queryset.filter(**{campo: valor})

        cliente = self.request.query_params.get("cliente")
        if cliente is not None:
            if not cliente.isdigit():
                raise serializers.ValidationError(
                    {"cliente": "Debe indicar un identificador numerico."},
                )
            queryset = queryset.filter(cliente_id=int(cliente))

        for parametro, lookup in (
            ("desde", "creado_en__date__gte"),
            ("hasta", "creado_en__date__lte"),
        ):
            valor_fecha = self.request.query_params.get(parametro)
            if valor_fecha is None:
                continue
            fecha = parse_date(valor_fecha)
            if fecha is None:
                raise serializers.ValidationError(
                    {parametro: "Use una fecha valida con formato AAAA-MM-DD."},
                )
            queryset = queryset.filter(**{lookup: fecha})
        return queryset

    @action(detail=True, methods=("post",), url_path="cambiar-estado")
    def cambiar_estado(self, request: Request, pk: str | None = None) -> Response:
        """Aplica una transicion de pedido con control de stock."""
        pedido_actual = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pedido = cambiar_estado_pedido(
                pedido_id=pedido_actual.pk,
                nuevo_estado=serializer.validated_data["estado"],
                comentario=serializer.validated_data.get("comentario", ""),
                usuario=request.user,
            )
        except TransicionPedidoError as error:
            return Response(
                {"estado": [str(error)]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._respuesta_pedido(pedido, request)

    @action(detail=True, methods=("post",), url_path="cambiar-estado-pago")
    def cambiar_estado_pago(
        self,
        request: Request,
        pk: str | None = None,
    ) -> Response:
        """Aplica una transicion de cobro y registra quien la realizo."""
        pedido_actual = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pedido = cambiar_estado_pago_pedido(
                pedido_id=pedido_actual.pk,
                nuevo_estado=serializer.validated_data["estado_pago"],
                comentario=serializer.validated_data.get("comentario", ""),
                usuario=request.user,
            )
        except TransicionPedidoError as error:
            return Response(
                {"estado_pago": [str(error)]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return self._respuesta_pedido(pedido, request)

    @staticmethod
    def _respuesta_pedido(pedido: Pedido, request: Request) -> Response:
        """Recarga relaciones para responder sin consultas repetitivas."""
        pedido_completo = (
            Pedido.objects.select_related("cliente")
            .prefetch_related("detalles__producto", "eventos__usuario")
            .get(pk=pedido.pk)
        )
        return Response(
            PedidoSerializer(
                pedido_completo,
                context={"request": request},
            ).data,
        )


class DetallePedidoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de solo lectura para detalles de pedidos."""

    permission_classes = (EsOperadorOAdmin,)
    serializer_class = DetallePedidoSerializer
    pagination_class = PaginacionPedidosInternos

    def get_queryset(self) -> QuerySet[DetallePedido]:
        queryset = DetallePedido.objects.select_related("pedido", "producto")
        pedido = self.request.query_params.get("pedido")
        if pedido is not None:
            if not pedido.isdigit():
                raise serializers.ValidationError(
                    {"pedido": "Debe indicar un identificador numerico."},
                )
            queryset = queryset.filter(pedido_id=int(pedido))
        return queryset


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
        serializer = PedidoPublicoCreateSerializer(
            data=request.data,
            context={"request": request},
        )
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
