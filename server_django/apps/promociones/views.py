"""Vistas publicas y de gestion de promociones."""

# pylint: disable=too-many-ancestors

from django.db.models import Q, QuerySet
from django.utils import timezone
from rest_framework import filters, serializers, viewsets
from rest_framework.pagination import PageNumberPagination

from apps.clientes.permissions import EsOperadorOAdmin
from apps.promociones.models import Promocion
from apps.promociones.serializers import (
    PromocionGestionSerializer,
    PromocionSerializer,
)


class PromocionViewSet(viewsets.ReadOnlyModelViewSet):
    """API publica limitada a promociones activas y vigentes."""

    serializer_class = PromocionSerializer

    def get_queryset(self) -> QuerySet[Promocion]:
        ahora = timezone.now()
        return Promocion.objects.filter(
            activa=True,
            fecha_inicio__lte=ahora,
            fecha_fin__gte=ahora,
        ).prefetch_related(
            "productos",
            "categorias",
            "items_combo__producto",
        )


class PaginacionPromociones(PageNumberPagination):
    """Paginacion acotada para el historial promocional."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class PromocionGestionViewSet(viewsets.ModelViewSet):
    """Gestion interna de alcance, vigencia y composicion de promociones."""

    http_method_names = ("get", "post", "patch", "head", "options")
    permission_classes = (EsOperadorOAdmin,)
    serializer_class = PromocionGestionSerializer
    pagination_class = PaginacionPromociones
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("nombre", "slug", "descripcion")
    ordering_fields = ("nombre", "fecha_inicio", "fecha_fin", "creada_en")
    ordering = ("-fecha_inicio", "nombre")

    def get_queryset(self) -> QuerySet[Promocion]:
        queryset = Promocion.objects.prefetch_related(
            "productos",
            "categorias",
            "items_combo__producto",
        )
        filtros_eleccion = {
            "tipo_promocion": set(Promocion.TipoPromocion.values),
            "canal_venta": set(Promocion.CanalVenta.values),
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

        activa = self.request.query_params.get("activa")
        if activa is not None:
            valores = {"true": True, "1": True, "false": False, "0": False}
            normalizado = activa.lower()
            if normalizado not in valores:
                raise serializers.ValidationError(
                    {"activa": "Use true, false, 1 o 0."},
                )
            queryset = queryset.filter(activa=valores[normalizado])

        vigente = self.request.query_params.get("vigente")
        if vigente is not None:
            valores_vigencia = {
                "true": True,
                "1": True,
                "false": False,
                "0": False,
            }
            normalizado = vigente.lower()
            if normalizado not in valores_vigencia:
                raise serializers.ValidationError(
                    {"vigente": "Use true, false, 1 o 0."},
                )
            ahora = timezone.now()
            consulta_vigente = Q(
                activa=True,
                fecha_inicio__lte=ahora,
                fecha_fin__gte=ahora,
            )
            queryset = (
                queryset.filter(consulta_vigente)
                if valores_vigencia[normalizado]
                else queryset.exclude(consulta_vigente)
            )
        return queryset
