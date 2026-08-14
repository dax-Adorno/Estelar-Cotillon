"""Rutas API de clientes."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.clientes.views import ClienteViewSet

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="clientes")

urlpatterns = [
    path("", include(router.urls)),
]
