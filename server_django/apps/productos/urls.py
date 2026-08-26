"""Rutas API de productos."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.productos.views import (
    CategoriaGestionViewSet,
    CategoriaViewSet,
    ImagenProductoGestionViewSet,
    ProductoGestionViewSet,
    ProductoViewSet,
)

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categorias")
router.register("productos", ProductoViewSet, basename="productos")
router.register(
    "gestion/categorias",
    CategoriaGestionViewSet,
    basename="gestion-categorias",
)
router.register(
    "gestion/productos",
    ProductoGestionViewSet,
    basename="gestion-productos",
)
router.register(
    "gestion/imagenes-producto",
    ImagenProductoGestionViewSet,
    basename="gestion-imagenes-producto",
)

urlpatterns = [
    path("", include(router.urls)),
]
