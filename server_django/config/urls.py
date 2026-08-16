"""Configuracion principal de URLs."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.productos.urls")),
    path("api/v1/", include("apps.clientes.urls")),
    path("api/v1/", include("apps.pedidos.urls")),
    path("api/v1/", include("apps.promociones.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
