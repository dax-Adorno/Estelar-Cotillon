"""Rutas API de pedidos."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pedidos.views import DetallePedidoViewSet, PedidoViewSet

router = DefaultRouter()
router.register("pedidos", PedidoViewSet, basename="pedidos")
router.register("detalle-pedidos", DetallePedidoViewSet, basename="detalle-pedidos")

urlpatterns = [
    path("", include(router.urls)),
]
