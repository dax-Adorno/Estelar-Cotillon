"""Vistas publicas y de gestion del catalogo."""

# pylint: disable=too-many-ancestors
from django.db.models import Prefetch, Q, QuerySet
from rest_framework import (
    filters,
    serializers,
    viewsets,
)
from rest_framework.pagination import PageNumberPagination

from apps.clientes.permissions import EsOperadorOAdmin
from apps.productos.models import Categoria, ImagenProducto, Producto
from apps.productos.serializers import (
    CategoriaGestionSerializer,
    CategoriaSerializer,
    ImagenProductoGestionSerializer,
    ProductoGestionSerializer,
    ProductoSerializer,
)


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para categorias activas."""

    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.filter(activa=True)


class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """API de solo lectura para productos activos."""

    serializer_class = ProductoSerializer
    queryset = (
        Producto.objects.filter(activo=True, categoria__activa=True)
        .select_related("categoria")
        .prefetch_related(
            Prefetch(
                "imagenes",
                queryset=ImagenProducto.objects.filter(activa=True),
                to_attr="imagenes_publicas",
            ),
        )
    )


class PaginacionGestionCatalogo(PageNumberPagination):
    """Paginacion acotada para catalogos de gran volumen."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


def _filtrar_booleano(
    queryset: QuerySet,
    campo: str,
    valor: str | None,
) -> QuerySet:
    """Aplica filtros booleanos estrictos y evita valores ambiguos."""
    if valor is None:
        return queryset
    valores = {"true": True, "1": True, "false": False, "0": False}
    normalizado = valor.lower()
    if normalizado not in valores:
        raise serializers.ValidationError(
            {campo: "Use true, false, 1 o 0."},
        )
    return queryset.filter(**{campo: valores[normalizado]})


class CategoriaGestionViewSet(viewsets.ModelViewSet):
    """Gestion interna de categorias y su publicacion."""

    http_method_names = ("get", "post", "patch", "head", "options")
    permission_classes = (EsOperadorOAdmin,)
    serializer_class = CategoriaGestionSerializer
    pagination_class = PaginacionGestionCatalogo
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("nombre", "slug", "descripcion")
    ordering_fields = ("nombre", "creada_en", "actualizada_en")
    ordering = ("nombre",)

    def get_queryset(self) -> QuerySet[Categoria]:
        queryset = Categoria.objects.all()
        return _filtrar_booleano(
            queryset,
            "activa",
            self.request.query_params.get("activa"),
        )


class ProductoGestionViewSet(viewsets.ModelViewSet):
    """Gestion interna de productos, precios, stock y publicacion."""

    http_method_names = ("get", "post", "patch", "head", "options")
    permission_classes = (EsOperadorOAdmin,)
    serializer_class = ProductoGestionSerializer
    pagination_class = PaginacionGestionCatalogo
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("sku", "nombre", "slug", "descripcion")
    ordering_fields = (
        "sku",
        "nombre",
        "precio_minorista",
        "precio_mayorista",
        "stock",
        "creado_en",
        "actualizado_en",
    )
    ordering = ("nombre",)

    def get_queryset(self) -> QuerySet[Producto]:
        queryset = Producto.objects.select_related("categoria").prefetch_related(
            "imagenes",
        )
        categoria = self.request.query_params.get("categoria")
        if categoria is not None:
            if not categoria.isdigit():
                raise serializers.ValidationError(
                    {"categoria": "Debe indicar un identificador numerico."},
                )
            queryset = queryset.filter(categoria_id=int(categoria))
        queryset = _filtrar_booleano(
            queryset,
            "activo",
            self.request.query_params.get("activo"),
        )
        queryset = _filtrar_booleano(
            queryset,
            "destacado",
            self.request.query_params.get("destacado"),
        )
        con_stock = self.request.query_params.get("con_stock")
        if con_stock is not None:
            valores = {"true": True, "1": True, "false": False, "0": False}
            normalizado = con_stock.lower()
            if normalizado not in valores:
                raise serializers.ValidationError(
                    {"con_stock": "Use true, false, 1 o 0."},
                )
            consulta_stock = Q(stock__gt=0) if valores[normalizado] else Q(stock=0)
            queryset = queryset.filter(consulta_stock)
        return queryset


class ImagenProductoGestionViewSet(viewsets.ModelViewSet):
    """Gestion interna de archivos y orden de imagenes."""

    http_method_names = ("get", "post", "patch", "delete", "head", "options")
    permission_classes = (EsOperadorOAdmin,)
    serializer_class = ImagenProductoGestionSerializer
    pagination_class = PaginacionGestionCatalogo
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ("orden", "creada_en", "actualizada_en")
    ordering = ("producto_id", "orden", "id")

    def get_queryset(self) -> QuerySet[ImagenProducto]:
        queryset = ImagenProducto.objects.select_related("producto")
        producto = self.request.query_params.get("producto")
        if producto is not None:
            if not producto.isdigit():
                raise serializers.ValidationError(
                    {"producto": "Debe indicar un identificador numerico."},
                )
            queryset = queryset.filter(producto_id=int(producto))
        return _filtrar_booleano(
            queryset,
            "activa",
            self.request.query_params.get("activa"),
        )
