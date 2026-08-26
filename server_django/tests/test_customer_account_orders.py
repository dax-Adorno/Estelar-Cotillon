"""Pruebas de cuenta e historial privado de pedidos."""

from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.clientes.models import Cliente, PerfilUsuario
from apps.pedidos.models import Pedido


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    return APIClient()


@pytest.fixture(name="customer_account")
def fixture_customer_account() -> tuple[Any, Cliente]:
    cliente = Cliente.objects.create(
        nombre="Ana",
        apellido="Gomez",
        email="ana@example.com",
        whatsapp="0981123456",
    )
    usuario = get_user_model().objects.create_user(
        username="ana@example.com",
        email="ana@example.com",
        password="test-password",
        first_name="Ana",
        last_name="Gomez",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        cliente=cliente,
        rol=PerfilUsuario.Rol.CLIENTE_MINORISTA,
    )
    return usuario, cliente


@pytest.mark.django_db
def test_mi_cuenta_requiere_autenticacion(api_client: APIClient) -> None:
    response = api_client.get("/api/v1/mi-cuenta/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cliente_actualiza_solo_sus_datos_editables(
    api_client: APIClient,
    customer_account: tuple[Any, Cliente],
) -> None:
    usuario, cliente = customer_account
    api_client.force_authenticate(user=usuario)

    response = api_client.patch(
        "/api/v1/mi-cuenta/",
        {
            "nombre": "Ana Maria",
            "apellido": "Gomez Duarte",
            "ciudad": "Asuncion",
            "email": "intento@example.com",
            "tipo_cliente": Cliente.TipoCliente.MAYORISTA,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    cliente.refresh_from_db()
    usuario.refresh_from_db()
    assert cliente.nombre == "Ana Maria"
    assert cliente.ciudad == "Asuncion"
    assert cliente.email == "ana@example.com"
    assert cliente.tipo_cliente == Cliente.TipoCliente.MINORISTA
    assert usuario.first_name == "Ana Maria"
    assert usuario.last_name == "Gomez Duarte"


@pytest.mark.django_db
def test_cliente_ve_solo_sus_pedidos(
    api_client: APIClient,
    customer_account: tuple[Any, Cliente],
) -> None:
    usuario, cliente = customer_account
    otro_cliente = Cliente.objects.create(nombre="Otro cliente")
    pedido_propio = Pedido.objects.create(
        cliente=cliente,
        codigo="PED-PROPIO",
        subtotal=Decimal("1000.00"),
        total=Decimal("1000.00"),
    )
    pedido_ajeno = Pedido.objects.create(
        cliente=otro_cliente,
        codigo="PED-AJENO",
        subtotal=Decimal("9000.00"),
        total=Decimal("9000.00"),
    )
    api_client.force_authenticate(user=usuario)

    response = api_client.get("/api/v1/mis-pedidos/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["codigo"] == pedido_propio.codigo

    response_ajeno = api_client.get(f"/api/v1/mis-pedidos/{pedido_ajeno.pk}/")
    assert response_ajeno.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_historial_esta_paginado(
    api_client: APIClient,
    customer_account: tuple[Any, Cliente],
) -> None:
    usuario, cliente = customer_account
    Pedido.objects.bulk_create(
        [
            Pedido(
                cliente=cliente,
                codigo=f"PED-{indice:03d}",
                subtotal=Decimal("1000.00"),
                total=Decimal("1000.00"),
            )
            for indice in range(21)
        ],
    )
    api_client.force_authenticate(user=usuario)

    response = api_client.get("/api/v1/mis-pedidos/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 21
    assert len(response.data["results"]) == 20
    assert response.data["next"] is not None


@pytest.mark.django_db
def test_operador_no_usa_endpoints_de_cliente(api_client: APIClient) -> None:
    usuario = get_user_model().objects.create_user(
        username="operador@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.OPERADOR,
    )
    api_client.force_authenticate(user=usuario)

    assert api_client.get("/api/v1/mi-cuenta/").status_code == 403
    assert api_client.get("/api/v1/mis-pedidos/").status_code == 403
