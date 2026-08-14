"""Tests para API de productos."""

# pylint: disable=duplicate-code

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.productos.models import Categoria, Producto


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Cliente HTTP para tests de API."""

    return APIClient()


@pytest.fixture(name="categoria")
def fixture_categoria() -> Categoria:
    """Crea una categoria activa para tests."""

    return Categoria.objects.create(
        nombre="Limpiapipas",
        slug="limpiapipas",
    )


@pytest.mark.django_db
def test_api_lista_categorias_activas(api_client: APIClient) -> None:
    Categoria.objects.create(
        nombre="Limpiapipas",
        slug="limpiapipas",
        activa=True,
    )
    Categoria.objects.create(
        nombre="Categoria inactiva",
        slug="categoria-inactiva",
        activa=False,
    )

    response = api_client.get(reverse("categorias-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["nombre"] == "Limpiapipas"


@pytest.mark.django_db
def test_api_lista_productos_activos(
    api_client: APIClient,
    categoria: Categoria,
) -> None:
    Producto.objects.create(
        categoria=categoria,
        sku="LIM-001",
        nombre="Limpiapipas surtidos",
        slug="limpiapipas-surtidos",
        precio_minorista=Decimal("1500.00"),
        precio_mayorista=Decimal("1200.00"),
        stock=50,
        activo=True,
    )
    Producto.objects.create(
        categoria=categoria,
        sku="LIM-002",
        nombre="Producto inactivo",
        slug="producto-inactivo",
        precio_minorista=Decimal("1000.00"),
        precio_mayorista=Decimal("800.00"),
        stock=10,
        activo=False,
    )

    response = api_client.get(reverse("productos-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["sku"] == "LIM-001"
    assert response.data[0]["categoria_nombre"] == "Limpiapipas"


@pytest.mark.django_db
def test_api_obtiene_detalle_producto(
    api_client: APIClient,
    categoria: Categoria,
) -> None:
    producto = Producto.objects.create(
        categoria=categoria,
        sku="KIT-001",
        nombre="Kit slime inicial",
        slug="kit-slime-inicial",
        precio_minorista=Decimal("2500.00"),
        precio_mayorista=Decimal("2000.00"),
        stock=20,
        activo=True,
    )

    response = api_client.get(
        reverse(
            "productos-detail",
            kwargs={"pk": producto.pk},
        ),
    )

    assert response.status_code == 200
    assert response.data["sku"] == "KIT-001"
    assert response.data["nombre"] == "Kit slime inicial"
