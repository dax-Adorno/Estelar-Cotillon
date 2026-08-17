"""Tests del panel administrativo de pedidos."""

from decimal import Decimal

import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from apps.clientes.models import Cliente
from apps.pedidos.admin import DetallePedidoInline, PedidoAdmin
from apps.pedidos.models import DetallePedido, Pedido
from apps.productos.models import Categoria, Producto


@pytest.fixture(name="pedido_con_detalle")
def fixture_pedido_con_detalle() -> Pedido:
    """Crea un pedido con detalle para probar el admin."""
    cliente = Cliente.objects.create(
        nombre="Cliente",
        apellido="Admin",
        email="cliente.admin@example.com",
        whatsapp="3764000000",
        telefono="3764000000",
        tipo_cliente=Cliente.TipoCliente.MINORISTA,
    )

    categoria = Categoria.objects.create(
        nombre="Categoría admin",
        slug="categoria-admin",
        descripcion="",
    )

    producto = Producto.objects.create(
        categoria=categoria,
        sku="ADM-PED-001",
        nombre="Producto admin pedido",
        slug="producto-admin-pedido",
        descripcion="Producto para test admin.",
        precio_minorista=Decimal("2500.00"),
        precio_mayorista=Decimal("2000.00"),
        cantidad_minima_mayorista=10,
        stock=30,
        activo=True,
        destacado=True,
    )

    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-ADMIN-001",
        estado=Pedido.EstadoPedido.PENDIENTE,
        estado_pago=Pedido.EstadoPago.PENDIENTE,
        canal_venta=Pedido.CanalVenta.WEB,
        subtotal=Decimal("5000.00"),
        descuento=Decimal("0.00"),
        total=Decimal("5000.00"),
    )

    DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=2,
        precio_unitario=Decimal("2500.00"),
        subtotal=Decimal("5000.00"),
    )

    return pedido


@pytest.mark.django_db
def test_pedido_admin_calcula_items_y_unidades(
    pedido_con_detalle: Pedido,
) -> None:
    """Debe mostrar cantidad de items y unidades del pedido."""
    pedido_admin = PedidoAdmin(Pedido, AdminSite())

    assert pedido_admin.cantidad_items(pedido_con_detalle) == 1
    assert pedido_admin.cantidad_unidades(pedido_con_detalle) == 2


@pytest.mark.django_db
def test_pedido_admin_optimiza_queryset(
    pedido_con_detalle: Pedido,
) -> None:
    """Debe devolver pedidos desde el queryset optimizado."""
    request = RequestFactory().get("/admin/pedidos/pedido/")
    pedido_admin = PedidoAdmin(Pedido, AdminSite())

    queryset = pedido_admin.get_queryset(request)

    assert pedido_con_detalle in queryset


@pytest.mark.django_db
def test_detalle_pedido_inline_no_permite_alta_ni_baja_manual(
    pedido_con_detalle: Pedido,
) -> None:
    """El inline no debe permitir agregar ni borrar detalles manualmente."""
    request = RequestFactory().get("/admin/pedidos/pedido/")
    inline = DetallePedidoInline(Pedido, AdminSite())

    assert inline.has_add_permission(request, pedido_con_detalle) is False
    assert inline.has_delete_permission(request, pedido_con_detalle) is False
