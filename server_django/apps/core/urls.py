from django.urls import path
from apps.core.reportes import ResumenComercialAPIView
from apps.core.views import healthcheck

urlpatterns = [
    path("health/", healthcheck, name="healthcheck"),
    path(
        "reportes/resumen-comercial/",
        ResumenComercialAPIView.as_view(),
        name="resumen-comercial",
    ),
]
