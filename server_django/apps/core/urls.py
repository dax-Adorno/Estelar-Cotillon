from django.urls import path
from apps.core.reportes import ResumenComercialAPIView
from apps.core.views import healthcheck, readiness_check

urlpatterns = [
    path("health/", healthcheck, name="healthcheck"),
    path("health/ready/", readiness_check, name="readiness-check"),
    path(
        "reportes/resumen-comercial/",
        ResumenComercialAPIView.as_view(),
        name="resumen-comercial",
    ),
]
