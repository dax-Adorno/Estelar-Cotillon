"""Tests para API publica de pedidos."""

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.clientes.models import Cliente
from apps.pedidos.models import DetallePedido, Pedido
from apps.productos.models import Categoria, Producto


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Cliente API para tests."""
    return APIClient()


@pytest.fixture(name="producto")
def fixture_producto() -> Producto:
    """Producto activo para pedido publico."""
    categoria = Categoria.objects.create(
        nombre="Categoria pedido",
        slug="categoria-pedido",
        descripcion="",
    )

    return Producto.objects.create(
        categoria=categoria,
        sku="PED-PUB-001",
        nombre="Producto pedido publico",
        slug="producto-pedido-publico",
        descripcion="Producto para test de pedido publico.",
        precio_minorista=Decimal("1500.00"),
        precio_mayorista=Decimal("1200.00"),
        cantidad_minima_mayorista=10,
        stock=50,
        activo=True,
        destacado=True,
    )


@pytest.mark.django_db
def test_crear_pedido_publico_desde_frontend(
    api_client: APIClient,
    producto: Producto,
) -> None:
    """Debe crear cliente, pedido y detalle desde endpoint publico."""
    payload = {
        "nombre_completo": "Cliente Web",
        "email": "cliente@example.com",
        "whatsapp": "3764000000",
        "notas": "Pedido desde catalogo web.",
        "items": [
            {
                "producto_id": producto.id,
                "cantidad": 2,
            }
        ],
    }

    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Pedido.objects.count() == 1
    assert DetallePedido.objects.count() == 1
    assert Cliente.objects.count() == 1

    pedido = Pedido.objects.get()

    assert pedido.codigo.startswith("PED-")
    assert pedido.estado == Pedido.EstadoPedido.PENDIENTE
    assert pedido.estado_pago == Pedido.EstadoPago.PENDIENTE
    assert pedido.canal_venta == Pedido.CanalVenta.WEB
    assert pedido.subtotal == Decimal("3000.00")
    assert pedido.total == Decimal("3000.00")

    detalle = DetallePedido.objects.get()

    assert detalle.producto == producto
    assert detalle.cantidad == 2
    assert detalle.precio_unitario == Decimal("1500.00")
    assert detalle.subtotal == Decimal("3000.00")


@pytest.mark.django_db
def test_crear_pedido_publico_rechaza_carrito_vacio(
    api_client: APIClient,
) -> None:
    """Debe rechazar pedidos sin items."""
    payload = {
        "nombre_completo": "Cliente Web",
        "email": "cliente@example.com",
        "whatsapp": "3764000000",
        "notas": "",
        "items": [],
    }

    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Pedido.objects.count() == 0


@pytest.mark.django_db
def test_crear_pedido_publico_rechaza_producto_inactivo(
    api_client: APIClient,
    producto: Producto,
) -> None:
    """Debe rechazar productos inactivos."""
    producto.activo = False
    producto.save(update_fields=["activo"])

    payload = {
        "nombre_completo": "Cliente Web",
        "email": "cliente@example.com",
        "whatsapp": "3764000000",
        "notas": "",
        "items": [
            {
                "producto_id": producto.id,
                "cantidad": 1,
            }
        ],
    }

    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Pedido.objects.count() == 0
