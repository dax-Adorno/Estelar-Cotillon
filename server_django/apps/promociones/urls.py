"""Rutas API de promociones."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.promociones.views import PromocionViewSet

router = DefaultRouter()
router.register("promociones", PromocionViewSet, basename="promociones")

urlpatterns = [
    path("", include(router.urls)),
]
