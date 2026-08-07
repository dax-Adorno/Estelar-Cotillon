import pytest
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
