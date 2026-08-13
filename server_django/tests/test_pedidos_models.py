"""Tests para modelos de pedidos."""

from decimal import Decimal

import pytest

from apps.clientes.models import Cliente
from apps.pedidos.models import DetallePedido, Pedido
from apps.productos.models import Categoria, Producto


@pytest.fixture(name="cliente")
def fixture_cliente() -> Cliente:
    """Crea un cliente base para tests de pedidos."""

    return Cliente.objects.create(
        nombre="Ana",
        apellido="Gomez",
    )


@pytest.fixture(name="producto")
def fixture_producto() -> Producto:
    """Crea un producto base para tests de pedidos."""

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
def test_pedido_str_devuelve_codigo(cliente: Cliente) -> None:
    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-001",
    )

    assert str(pedido) == "PED-001"


@pytest.mark.django_db
def test_pedido_calcula_total_con_descuento(cliente: Cliente) -> None:
    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-002",
        subtotal=Decimal("10000.00"),
        descuento=Decimal("1500.00"),
    )

    assert pedido.calcular_total() == Decimal("8500.00")


@pytest.mark.django_db
def test_pedido_no_permite_total_negativo(cliente: Cliente) -> None:
    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-003",
        subtotal=Decimal("1000.00"),
        descuento=Decimal("2000.00"),
    )

    assert pedido.calcular_total() == Decimal("0.00")


@pytest.mark.django_db
def test_detalle_pedido_calcula_subtotal(
    cliente: Cliente,
    producto: Producto,
) -> None:
    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-004",
    )

    detalle = DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=3,
        precio_unitario=Decimal("1500.00"),
        subtotal=Decimal("4500.00"),
    )

    assert detalle.calcular_subtotal() == Decimal("4500.00")
    assert pedido.detalles.count() == 1


@pytest.mark.django_db
def test_detalle_pedido_str_devuelve_codigo_y_producto(
    cliente: Cliente,
    producto: Producto,
) -> None:
    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-005",
    )

    detalle = DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=1,
        precio_unitario=Decimal("1500.00"),
        subtotal=Decimal("1500.00"),
    )

    assert str(detalle) == "PED-005 - Limpiapipas surtidos"
