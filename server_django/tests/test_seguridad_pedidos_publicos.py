"""Tests de seguridad para pedidos publicos."""

from decimal import Decimal

import pytest
from django.core.cache import cache
from pytest import MonkeyPatch
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.throttles import PedidoPublicoAnonRateThrottle
from apps.productos.models import Categoria, Producto


@pytest.fixture(autouse=True)
def limpiar_cache() -> None:
    """Limpia cache para aislar pruebas de throttle."""
    cache.clear()


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Cliente API para tests."""
    return APIClient()


@pytest.fixture(name="producto")
def fixture_producto() -> Producto:
    """Producto activo para prueba de seguridad."""
    categoria = Categoria.objects.create(
        nombre="Categoria seguridad",
        slug="categoria-seguridad",
        descripcion="",
    )

    return Producto.objects.create(
        categoria=categoria,
        sku="SEG-001",
        nombre="Producto seguridad",
        slug="producto-seguridad",
        descripcion="Producto para test de throttle.",
        precio_minorista=Decimal("1000.00"),
        precio_mayorista=Decimal("800.00"),
        cantidad_minima_mayorista=10,
        stock=50,
        activo=True,
        destacado=True,
    )


def _payload_pedido(producto: Producto) -> dict:
    """Payload valido para crear pedido publico."""
    return {
        "nombre_completo": "Cliente Seguridad",
        "email": "cliente.seguridad@example.com",
        "whatsapp": "3764000000",
        "notas": "",
        "items": [
            {
                "producto_id": producto.id,
                "cantidad": 1,
            },
        ],
    }


@pytest.mark.django_db
def test_pedido_publico_aplica_rate_limit(
    api_client: APIClient,
    producto: Producto,
    monkeypatch: MonkeyPatch,
) -> None:
    """Debe limitar multiples pedidos anonimos en poco tiempo."""
    monkeypatch.setattr(
        PedidoPublicoAnonRateThrottle,
        "THROTTLE_RATES",
        {
            "pedidos_publicos": "1/min",
        },
    )

    payload = _payload_pedido(producto)

    primera_respuesta = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload,
        format="json",
    )
    segunda_respuesta = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload,
        format="json",
    )

    assert primera_respuesta.status_code == status.HTTP_201_CREATED
    assert segunda_respuesta.status_code == status.HTTP_429_TOO_MANY_REQUESTS
