"""Tests para API de clientes."""

# pylint: disable=duplicate-code

from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.clientes.models import Cliente, PerfilUsuario
from apps.pedidos.models import Pedido


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Cliente HTTP para tests de API."""

    return APIClient()


@pytest.fixture(name="admin_user")
def fixture_admin_user() -> Any:
    """Usuario admin para acceder a endpoints protegidos."""

    user_model = get_user_model()

    return user_model.objects.create_user(
        username="admin",
        password="test-password",
        is_staff=True,
    )


@pytest.mark.django_db
def test_api_clientes_requiere_usuario_admin(api_client: APIClient) -> None:
    response = api_client.get(reverse("clientes-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_api_lista_clientes_activos_para_admin(
    api_client: APIClient,
    admin_user: Any,
) -> None:
    Cliente.objects.create(
        nombre="Ana",
        apellido="Gomez",
        email="ana@example.com",
        activo=True,
    )
    Cliente.objects.create(
        nombre="Cliente",
        apellido="Inactivo",
        email="inactivo@example.com",
        activo=False,
    )

    api_client.force_authenticate(user=admin_user)

    response = api_client.get(reverse("clientes-list"))

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["nombre"] == "Ana"
    assert response.data["results"][0]["activo"] is True


@pytest.mark.django_db
def test_api_obtiene_detalle_cliente_para_admin(
    api_client: APIClient,
    admin_user: Any,
) -> None:
    cliente = Cliente.objects.create(
        nombre="Carolina",
        apellido="Lopez",
        tipo_cliente=Cliente.TipoCliente.MAYORISTA,
        whatsapp="3764000000",
    )

    api_client.force_authenticate(user=admin_user)

    response = api_client.get(
        reverse(
            "clientes-detail",
            kwargs={"pk": cliente.pk},
        ),
    )

    assert response.status_code == 200
    assert response.data["nombre"] == "Carolina"
    assert response.data["tipo_cliente"] == Cliente.TipoCliente.MAYORISTA
    assert response.data["whatsapp"] == "3764000000"


@pytest.mark.django_db
def test_api_segmenta_mayoristas_y_resume_su_actividad(
    api_client: APIClient,
    admin_user: Any,
) -> None:
    cliente = Cliente.objects.create(
        nombre="Mayorista",
        razon_social="Fiestas SA",
        email="mayorista-listado@example.com",
        tipo_cliente=Cliente.TipoCliente.MAYORISTA,
    )
    usuario = get_user_model().objects.create_user(
        username="mayorista-listado@example.com",
        email="mayorista-listado@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        cliente=cliente,
        rol=PerfilUsuario.Rol.CLIENTE_MAYORISTA,
        mayorista_aprobado=False,
    )
    Pedido.objects.create(
        cliente=cliente,
        codigo="CLI-METRICAS-001",
        estado=Pedido.EstadoPedido.ENTREGADO,
        total=Decimal("125000.00"),
    )
    Pedido.objects.create(
        cliente=cliente,
        codigo="CLI-METRICAS-CANCELADO",
        estado=Pedido.EstadoPedido.CANCELADO,
        total=Decimal("50000.00"),
    )
    api_client.force_authenticate(user=admin_user)

    response = api_client.get(
        reverse("clientes-list"),
        {"cuenta": "mayorista_pendiente", "search": "Fiestas"},
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    resumen = response.data["results"][0]
    assert resumen["perfil_id"] is not None
    assert resumen["rol"] == PerfilUsuario.Rol.CLIENTE_MAYORISTA
    assert resumen["mayorista_aprobado"] is False
    assert resumen["pedidos_total"] == 1
    assert resumen["total_comprado"] == "125000.00"
    assert resumen["ultimo_pedido_en"] is not None
