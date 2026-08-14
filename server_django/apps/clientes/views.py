"""Vistas API de clientes."""

# pylint: disable=too-many-ancestors

from rest_framework import permissions, viewsets

from apps.clientes.models import Cliente
from apps.clientes.serializers import ClienteSerializer


class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para clientes activos."""

    serializer_class = ClienteSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = Cliente.objects.filter(activo=True)
