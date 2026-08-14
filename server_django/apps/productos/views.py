"""Vistas API de productos."""

# pylint: disable=too-many-ancestors
from rest_framework import viewsets

from apps.productos.models import Categoria, Producto
from apps.productos.serializers import CategoriaSerializer, ProductoSerializer


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para categorias activas."""

    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.filter(activa=True)


class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para productos activos."""

    serializer_class = ProductoSerializer
    queryset = Producto.objects.filter(activo=True).select_related("categoria")
