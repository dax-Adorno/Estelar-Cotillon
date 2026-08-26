"""Rutas API de pedidos."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pedidos.views import (
    DetallePedidoViewSet,
    MisPedidosViewSet,
    PedidoPublicoCreateAPIView,
    PedidoViewSet,
)

router = DefaultRouter()
router.register("pedidos", PedidoViewSet, basename="pedidos")
router.register("detalle-pedidos", DetallePedidoViewSet, basename="detalle-pedidos")
router.register("mis-pedidos", MisPedidosViewSet, basename="mis-pedidos")

urlpatterns = [
    path("pedidos-publicos/", PedidoPublicoCreateAPIView.as_view()),
    path("", include(router.urls)),
]
