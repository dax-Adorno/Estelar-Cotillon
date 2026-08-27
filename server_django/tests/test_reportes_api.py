"""Tests para reportes comerciales internos."""

from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.clientes.models import Cliente, PerfilUsuario
from apps.pedidos.models import DetallePedido, Pedido
from apps.productos.models import Categoria, Producto


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Cliente API para tests."""
    return APIClient()


@pytest.fixture(name="admin_user")
def fixture_admin_user() -> Any:
    """Usuario administrador para acceder a reportes."""
    usuario_modelo = get_user_model()

    return usuario_modelo.objects.create_superuser(
        username="admin_reportes",
        email="admin.reportes@example.com",
        password="test-password",
    )


@pytest.fixture(name="pedido_reportado")
def fixture_pedido_reportado() -> Pedido:
    """Pedido con detalle para alimentar metricas."""
    cliente = Cliente.objects.create(
        nombre="Cliente",
        apellido="Reporte",
        email="cliente.reporte@example.com",
        whatsapp="3764000000",
        telefono="3764000000",
        tipo_cliente=Cliente.TipoCliente.MINORISTA,
    )

    categoria = Categoria.objects.create(
        nombre="Categoría reporte",
        slug="categoria-reporte",
        descripcion="",
        activa=True,
    )

    producto = Producto.objects.create(
        categoria=categoria,
        sku="REP-001",
        nombre="Producto reporte",
        slug="producto-reporte",
        descripcion="Producto para reporte.",
        precio_minorista=Decimal("1000.00"),
        precio_mayorista=Decimal("800.00"),
        cantidad_minima_mayorista=10,
        stock=5,
        activo=True,
        destacado=True,
    )

    pedido = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-REPORTE-001",
        estado=Pedido.EstadoPedido.PENDIENTE,
        estado_pago=Pedido.EstadoPago.PENDIENTE,
        canal_venta=Pedido.CanalVenta.WEB,
        subtotal=Decimal("3000.00"),
        descuento=Decimal("0.00"),
        total=Decimal("3000.00"),
    )

    DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=3,
        precio_unitario=Decimal("1000.00"),
        subtotal=Decimal("3000.00"),
    )

    return pedido


@pytest.mark.django_db
def test_resumen_comercial_requiere_acceso_interno(
    api_client: APIClient,
) -> None:
    """Debe rechazar usuarios no autenticados."""
    response = api_client.get("/api/v1/reportes/resumen-comercial/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_resumen_comercial_permite_operador(
    api_client: APIClient,
) -> None:
    """Debe permitir consultar métricas a un operador autenticado."""
    usuario_modelo = get_user_model()
    operador = usuario_modelo.objects.create_user(
        username="operador_reportes",
        email="operador.reportes@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=operador,
        rol=PerfilUsuario.Rol.OPERADOR,
    )
    api_client.force_authenticate(user=operador)

    response = api_client.get("/api/v1/reportes/resumen-comercial/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["metricas"]["pedidos_total"] == 0


@pytest.mark.django_db
def test_resumen_comercial_devuelve_metricas_basicas(
    api_client: APIClient,
    admin_user: Any,
    pedido_reportado: Pedido,
) -> None:
    """Debe devolver metricas comerciales basicas."""
    api_client.force_authenticate(user=admin_user)

    response = api_client.get("/api/v1/reportes/resumen-comercial/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["generado_en"]
    assert data["stock_bajo_umbral"] == 10
    assert data["metricas"]["pedidos_total"] == 1
    assert data["metricas"]["pedidos_pendientes"] == 1
    assert data["metricas"]["total_estimado"] == "3000.00"
    assert data["metricas"]["unidades_pedidas"] == 3
    assert data["metricas"]["productos_activos"] == 1
    assert data["metricas"]["productos_stock_bajo"] == 1
    assert data["metricas"]["categorias_activas"] == 1

    assert data["pedidos_por_estado"] == [
        {
            "estado": Pedido.EstadoPedido.PENDIENTE,
            "cantidad": 1,
        },
    ]

    assert data["pedidos_por_canal"] == [
        {
            "canal_venta": Pedido.CanalVenta.WEB,
            "cantidad": 1,
        },
    ]

    assert data["top_productos"] == [
        {
            "producto_id": pedido_reportado.detalles.first().producto_id,
            "sku": "REP-001",
            "nombre": "Producto reporte",
            "unidades": 3,
            "importe": "3000.00",
        },
    ]

    assert data["productos_stock_bajo"] == [
        {
            "id": pedido_reportado.detalles.first().producto_id,
            "sku": "REP-001",
            "nombre": "Producto reporte",
            "stock": 5,
        },
    ]
