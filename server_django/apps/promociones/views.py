"""Vistas API de promociones."""

# pylint: disable=too-many-ancestors

from rest_framework import viewsets

from apps.promociones.models import Promocion
from apps.promociones.serializers import PromocionSerializer


class PromocionViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para promociones activas."""

    serializer_class = PromocionSerializer
    queryset = Promocion.objects.filter(activa=True).prefetch_related(
        "productos",
        "categorias",
    )
