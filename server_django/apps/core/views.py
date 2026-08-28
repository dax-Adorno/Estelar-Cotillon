from django.db import OperationalError, connections
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def healthcheck(request):
    return Response(
        {
            "estado": "ok",
            "servicio": "estelart-api",
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    """Confirma que la API puede aceptar tráfico y acceder a la base de datos."""

    try:
        connections["default"].ensure_connection()
    except OperationalError:
        return Response(
            {
                "estado": "no_disponible",
                "servicio": "estelart-api",
                "base_de_datos": "error",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        {
            "estado": "ok",
            "servicio": "estelart-api",
            "base_de_datos": "ok",
        }
    )
