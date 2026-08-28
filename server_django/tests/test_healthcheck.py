from unittest.mock import patch

import pytest
from django.db import OperationalError, connections
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_healthcheck_deberia_responder_ok():
    client = APIClient()

    response = client.get(reverse("healthcheck"))

    assert response.status_code == 200
    assert response.json() == {
        "estado": "ok",
        "servicio": "estelart-api",
    }


@pytest.mark.django_db
def test_readiness_deberia_confirmar_base_de_datos_disponible():
    response = APIClient().get(reverse("readiness-check"))

    assert response.status_code == 200
    assert response.json() == {
        "estado": "ok",
        "servicio": "estelart-api",
        "base_de_datos": "ok",
    }


@pytest.mark.django_db
def test_readiness_deberia_fallar_si_base_de_datos_no_responde():
    with patch.object(
        connections["default"],
        "ensure_connection",
        side_effect=OperationalError,
    ):
        response = APIClient().get(reverse("readiness-check"))

    assert response.status_code == 503
    assert response.json()["estado"] == "no_disponible"
