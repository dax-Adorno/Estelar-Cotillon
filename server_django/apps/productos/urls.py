"""Rutas API de productos."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.productos.views import CategoriaViewSet, ProductoViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categorias")
router.register("productos", ProductoViewSet, basename="productos")

urlpatterns = [
    path("", include(router.urls)),
]
