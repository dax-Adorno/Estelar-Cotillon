"""URL configuration for config project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.productos.urls")),
    path("api/v1/", include("apps.clientes.urls")),
    path("api/v1/", include("apps.pedidos.urls")),
]
