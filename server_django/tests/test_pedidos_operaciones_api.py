"""Pruebas del flujo operativo y auditable de pedidos."""

# pylint: disable=duplicate-code

from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.clientes.models import Cliente, PerfilUsuario
from apps.pedidos.models import DetallePedido, EventoPedido, Pedido
from apps.productos.models import Categoria, Producto


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    return APIClient()


@pytest.fixture(name="operator_user")
def fixture_operator_user() -> Any:
    usuario = get_user_model().objects.create_user(
        username="pedidos@example.com",
        email="pedidos@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.OPERADOR,
    )
    return usuario


@pytest.fixture(name="customer_user")
def fixture_customer_user() -> Any:
    usuario = get_user_model().objects.create_user(
        username="comprador@example.com",
        email="comprador@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.CLIENTE_MINORISTA,
    )
    return usuario


@pytest.fixture(name="cliente")
def fixture_cliente() -> Cliente:
    return Cliente.objects.create(
        nombre="Maria",
        apellido="Lopez",
        email="maria@example.com",
        whatsapp="0981000000",
    )


@pytest.fixture(name="producto")
def fixture_producto() -> Producto:
    categoria = Categoria.objects.create(
        nombre="Decoracion",
        slug="decoracion",
    )
    return Producto.objects.create(
        categoria=categoria,
        sku="DEC-001",
        nombre="Guirnalda",
        slug="guirnalda",
        precio_minorista=Decimal("10000.00"),
        precio_mayorista=Decimal("8000.00"),
        cantidad_minima_mayorista=5,
        stock=10,
    )


@pytest.fixture(name="pedido")
def fixture_pedido(cliente: Cliente, producto: Producto) -> Pedido:
    pedido_creado = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-OPS-001",
        estado=Pedido.EstadoPedido.PENDIENTE,
        estado_pago=Pedido.EstadoPago.PENDIENTE,
        canal_venta=Pedido.CanalVenta.WEB,
        subtotal=Decimal("20000.00"),
        total=Decimal("20000.00"),
    )
    DetallePedido.objects.create(
        pedido=pedido_creado,
        producto=producto,
        cantidad=2,
        precio_unitario=Decimal("10000.00"),
        subtotal=Decimal("20000.00"),
    )
    return pedido_creado


def ruta_estado(pedido: Pedido) -> str:
    return reverse("pedidos-cambiar-estado", kwargs={"pk": pedido.pk})


def ruta_estado_pago(pedido: Pedido) -> str:
    return reverse("pedidos-cambiar-estado-pago", kwargs={"pk": pedido.pk})


@pytest.mark.django_db
@pytest.mark.parametrize("autenticado", (False, True))
def test_cliente_no_puede_operar_pedidos(
    api_client: APIClient,
    customer_user: Any,
    pedido: Pedido,
    autenticado: bool,
) -> None:
    if autenticado:
        api_client.force_authenticate(user=customer_user)

    response = api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.CONFIRMADO},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_confirmar_pedido_descuenta_stock_y_registra_evento(
    api_client: APIClient,
    operator_user: Any,
    pedido: Pedido,
    producto: Producto,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        ruta_estado(pedido),
        {
            "estado": Pedido.EstadoPedido.CONFIRMADO,
            "comentario": "Stock verificado con deposito.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    pedido.refresh_from_db()
    producto.refresh_from_db()
    assert pedido.estado == Pedido.EstadoPedido.CONFIRMADO
    assert producto.stock == 8
    evento = EventoPedido.objects.get(pedido=pedido)
    assert evento.valor_anterior == Pedido.EstadoPedido.PENDIENTE
    assert evento.valor_nuevo == Pedido.EstadoPedido.CONFIRMADO
    assert evento.usuario == operator_user
    assert evento.comentario == "Stock verificado con deposito."
    assert response.data["eventos"][0]["usuario_email"] == "pedidos@example.com"


@pytest.mark.django_db
def test_confirmar_pedido_sin_stock_revierte_toda_la_operacion(
    api_client: APIClient,
    operator_user: Any,
    pedido: Pedido,
    producto: Producto,
) -> None:
    producto.stock = 1
    producto.save(update_fields=["stock"])
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.CONFIRMADO},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    pedido.refresh_from_db()
    producto.refresh_from_db()
    assert pedido.estado == Pedido.EstadoPedido.PENDIENTE
    assert producto.stock == 1
    assert EventoPedido.objects.filter(pedido=pedido).exists() is False


@pytest.mark.django_db
def test_cancelar_pedido_confirmado_repone_stock(
    api_client: APIClient,
    operator_user: Any,
    pedido: Pedido,
    producto: Producto,
) -> None:
    api_client.force_authenticate(user=operator_user)
    api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.CONFIRMADO},
        format="json",
    )

    response = api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.CANCELADO},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    producto.refresh_from_db()
    assert producto.stock == 10
    assert EventoPedido.objects.filter(pedido=pedido).count() == 2


@pytest.mark.django_db
def test_pedido_cobrado_exige_reembolso_antes_de_cancelar(
    api_client: APIClient,
    operator_user: Any,
    pedido: Pedido,
    producto: Producto,
) -> None:
    api_client.force_authenticate(user=operator_user)
    api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.CONFIRMADO},
        format="json",
    )
    pago = api_client.post(
        ruta_estado_pago(pedido),
        {"estado_pago": Pedido.EstadoPago.PAGADO},
        format="json",
    )

    cancelacion_invalida = api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.CANCELADO},
        format="json",
    )
    reembolso = api_client.post(
        ruta_estado_pago(pedido),
        {"estado_pago": Pedido.EstadoPago.REEMBOLSADO},
        format="json",
    )
    cancelacion_valida = api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.CANCELADO},
        format="json",
    )

    assert pago.status_code == status.HTTP_200_OK
    assert cancelacion_invalida.status_code == status.HTTP_400_BAD_REQUEST
    assert reembolso.status_code == status.HTTP_200_OK
    assert cancelacion_valida.status_code == status.HTTP_200_OK
    producto.refresh_from_db()
    assert producto.stock == 10


@pytest.mark.django_db
def test_transicion_invalida_no_modifica_pedido(
    api_client: APIClient,
    operator_user: Any,
    pedido: Pedido,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        ruta_estado(pedido),
        {"estado": Pedido.EstadoPedido.ENTREGADO},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    pedido.refresh_from_db()
    assert pedido.estado == Pedido.EstadoPedido.PENDIENTE


@pytest.mark.django_db
def test_listado_operativo_es_paginado_filtrable_y_liviano(
    api_client: APIClient,
    operator_user: Any,
    pedido: Pedido,
) -> None:
    Pedido.objects.create(
        cliente=pedido.cliente,
        codigo="PED-OPS-CANCELADO",
        estado=Pedido.EstadoPedido.CANCELADO,
        canal_venta=Pedido.CanalVenta.WHATSAPP,
    )
    api_client.force_authenticate(user=operator_user)

    response = api_client.get(
        reverse("pedidos-list"),
        {
            "estado": Pedido.EstadoPedido.PENDIENTE,
            "canal_venta": Pedido.CanalVenta.WEB,
            "search": "maria@example.com",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    resumen = response.data["results"][0]
    assert resumen["codigo"] == "PED-OPS-001"
    assert resumen["cantidad_items"] == 1
    assert resumen["cantidad_unidades"] == 2
    assert "detalles" not in resumen
    assert "eventos" not in resumen


@pytest.mark.django_db
def test_filtros_operativos_invalidos_devuelven_400(
    api_client: APIClient,
    operator_user: Any,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.get(
        reverse("pedidos-list"),
        {"estado": "inventado", "desde": "ayer"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "estado" in response.data


@pytest.mark.django_db
def test_checkout_rechaza_cantidad_superior_al_stock(
    api_client: APIClient,
    producto: Producto,
) -> None:
    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        {
            "nombre_completo": "Cliente sin stock",
            "email": "sin-stock@example.com",
            "whatsapp": "0981222333",
            "items": [{"producto_id": producto.pk, "cantidad": 11}],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Pedido.objects.exists() is False


@pytest.mark.django_db
def test_checkout_rechaza_producto_de_categoria_inactiva(
    api_client: APIClient,
    producto: Producto,
) -> None:
    producto.categoria.activa = False
    producto.categoria.save(update_fields=["activa"])

    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        {
            "nombre_completo": "Cliente categoria oculta",
            "email": "categoria-oculta@example.com",
            "whatsapp": "0981222444",
            "items": [{"producto_id": producto.pk, "cantidad": 1}],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Pedido.objects.exists() is False
