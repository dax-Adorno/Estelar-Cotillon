"""Tests para API de promociones."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.promociones.models import Promocion


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Cliente HTTP para tests de API."""

    return APIClient()


@pytest.mark.django_db
def test_api_lista_promociones_activas(api_client: APIClient) -> None:
    ahora = timezone.now()

    Promocion.objects.create(
        nombre="Promo activa",
        slug="promo-activa",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("10.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=7),
        activa=True,
    )
    Promocion.objects.create(
        nombre="Promo inactiva",
        slug="promo-inactiva",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("15.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=7),
        activa=False,
    )

    response = api_client.get(reverse("promociones-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["nombre"] == "Promo activa"


@pytest.mark.django_db
def test_api_indica_si_promocion_esta_vigente(api_client: APIClient) -> None:
    ahora = timezone.now()

    Promocion.objects.create(
        nombre="Promo vigente",
        slug="promo-vigente-api",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("20.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=1),
        activa=True,
    )

    response = api_client.get(reverse("promociones-list"))

    assert response.status_code == 200
    assert response.data[0]["vigente"] is True


@pytest.mark.django_db
def test_api_obtiene_detalle_promocion(api_client: APIClient) -> None:
    ahora = timezone.now()

    promocion = Promocion.objects.create(
        nombre="Promo mayorista",
        slug="promo-mayorista",
        tipo_promocion=Promocion.TipoPromocion.MAYORISTA,
        monto_descuento=Decimal("500.00"),
        compra_minima=Decimal("10000.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=10),
        activa=True,
    )

    response = api_client.get(
        reverse(
            "promociones-detail",
            kwargs={"pk": promocion.pk},
        ),
    )

    assert response.status_code == 200
    assert response.data["nombre"] == "Promo mayorista"
    assert response.data["tipo_promocion"] == Promocion.TipoPromocion.MAYORISTA
    assert response.data["monto_descuento"] == "500.00"
