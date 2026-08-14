"""Tests para API de pedidos."""

from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.clientes.models import Cliente
from apps.pedidos.models import DetallePedido, Pedido
from apps.productos.models import Categoria, Producto


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Cliente HTTP para tests de API."""

    return APIClient()


@pytest.fixture(name="admin_user")
def fixture_admin_user() -> Any:
    """Usuario admin para endpoints protegidos."""

    user_model = get_user_model()

    return user_model.objects.create_user(
        username="admin-pedidos",
        password="test-password",
        is_staff=True,
    )


@pytest.fixture(name="cliente")
def fixture_cliente() -> Cliente:
    """Cliente base."""

    return Cliente.objects.create(
        nombre="Ana",
        apellido="Gomez",
    )


@pytest.fixture(name="producto")
def fixture_producto() -> Producto:
    """Producto base."""

    categoria = Categoria.objects.create(
        nombre="Limpiapipas",
        slug="limpiapipas",
    )

    return Producto.objects.create(
        categoria=categoria,
        sku="LIM-001",
        nombre="Limpiapipas surtidos",
        slug="limpiapipas-surtidos",
        precio_minorista=Decimal("1500.00"),
        precio_mayorista=Decimal("1200.00"),
        stock=50,
    )


@pytest.mark.django_db
def test_api_pedidos_requiere_usuario_admin(api_client: APIClient) -> None:
    response = api_client.get(reverse("pedidos-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_api_lista_pedidos_para_admin(
    api_client: APIClient,
    admin_user: Any,
    cliente: Cliente,
) -> None:
    Pedido.objects.create(
        cliente=cliente,
        codigo="PED-001",
        estado=Pedido.EstadoPedido.CONFIRMADO,
        estado_pago=Pedido.EstadoPago.PAGADO,
        canal_venta=Pedido.CanalVenta.WHATSAPP,
        subtotal=Decimal("3000.00"),
        descuento=Decimal("0.00"),
        total=Decimal("3000.00"),
    )

    api_client.force_authenticate(user=admin_user)

    response = api_client.get(reverse("pedidos-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["codigo"] == "PED-001"
    assert response.data[0]["estado"] == Pedido.EstadoPedido.CONFIRMADO


@pytest.mark.django_db
def test_api_obtiene_detalle_pedido_con_lineas(
    api_client: APIClient,
    admin_user: Any,
    cliente: Cliente,
    producto: Producto,
) -> None:
    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-002",
        subtotal=Decimal("4500.00"),
        descuento=Decimal("0.00"),
        total=Decimal("4500.00"),
    )

    DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=3,
        precio_unitario=Decimal("1500.00"),
        subtotal=Decimal("4500.00"),
    )

    api_client.force_authenticate(user=admin_user)

    response = api_client.get(
        reverse(
            "pedidos-detail",
            kwargs={"pk": pedido.pk},
        ),
    )

    assert response.status_code == 200
    assert response.data["codigo"] == "PED-002"
    assert len(response.data["detalles"]) == 1
    assert response.data["detalles"][0]["producto_sku"] == "LIM-001"


@pytest.mark.django_db
def test_api_lista_detalle_pedidos_para_admin(
    api_client: APIClient,
    admin_user: Any,
    cliente: Cliente,
    producto: Producto,
) -> None:
    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-003",
    )

    DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=2,
        precio_unitario=Decimal("1500.00"),
        subtotal=Decimal("3000.00"),
    )

    api_client.force_authenticate(user=admin_user)

    response = api_client.get(reverse("detalle-pedidos-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["producto_nombre"] == "Limpiapipas surtidos"
