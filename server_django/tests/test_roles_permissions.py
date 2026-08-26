"""Pruebas de autorizacion por roles ESTELART."""

from typing import Any

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.clientes.models import Cliente, PerfilUsuario
from apps.clientes.permissions import EsMayoristaAprobado


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    return APIClient()


@pytest.fixture(name="admin_user")
def fixture_admin_user() -> Any:
    return get_user_model().objects.create_superuser(
        username="superadmin@example.com",
        email="superadmin@example.com",
        password="test-password",
    )


@pytest.fixture(name="operator_user")
def fixture_operator_user() -> Any:
    usuario = get_user_model().objects.create_user(
        username="operador@example.com",
        email="operador@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.OPERADOR,
    )
    return usuario


@pytest.fixture(name="minorista_user")
def fixture_minorista_user() -> Any:
    usuario = get_user_model().objects.create_user(
        username="minorista@example.com",
        email="minorista@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.CLIENTE_MINORISTA,
    )
    return usuario


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/clientes/",
        "/api/v1/pedidos/",
        "/api/v1/reportes/resumen-comercial/",
    ],
)
def test_operador_accede_a_recursos_internos(
    api_client: APIClient,
    operator_user: Any,
    endpoint: str,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.get(endpoint)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_minorista_no_accede_a_recursos_internos(
    api_client: APIClient,
    minorista_user: Any,
) -> None:
    api_client.force_authenticate(user=minorista_user)

    response = api_client.get("/api/v1/pedidos/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_operador_no_puede_gestionar_roles(
    api_client: APIClient,
    operator_user: Any,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.get("/api/v1/perfiles-usuario/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superadmin_aprueba_mayorista(
    api_client: APIClient,
    admin_user: Any,
) -> None:
    cliente = Cliente.objects.create(
        nombre="Mayorista",
        razon_social="Fiestas SA",
        email="mayorista@example.com",
        tipo_cliente=Cliente.TipoCliente.MAYORISTA,
    )
    usuario = get_user_model().objects.create_user(
        username="mayorista@example.com",
        email="mayorista@example.com",
        password="test-password",
    )
    perfil = PerfilUsuario.objects.create(
        usuario=usuario,
        cliente=cliente,
        rol=PerfilUsuario.Rol.CLIENTE_MAYORISTA,
        mayorista_aprobado=False,
    )
    api_client.force_authenticate(user=admin_user)

    response = api_client.patch(
        f"/api/v1/perfiles-usuario/{perfil.pk}/",
        {"mayorista_aprobado": True},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    perfil.refresh_from_db()
    assert perfil.mayorista_aprobado is True


@pytest.mark.django_db
def test_admin_no_superusuario_no_puede_crear_otro_admin(
    api_client: APIClient,
    minorista_user: Any,
) -> None:
    administrador = get_user_model().objects.create_user(
        username="admin@example.com",
        email="admin@example.com",
        password="test-password",
        is_staff=True,
    )
    PerfilUsuario.objects.create(
        usuario=administrador,
        rol=PerfilUsuario.Rol.ADMIN,
    )
    objetivo = minorista_user.perfil_estelart
    api_client.force_authenticate(user=administrador)

    response = api_client.patch(
        f"/api/v1/perfiles-usuario/{objetivo.pk}/",
        {"rol": PerfilUsuario.Rol.ADMIN},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    objetivo.refresh_from_db()
    assert objetivo.rol == PerfilUsuario.Rol.CLIENTE_MINORISTA


@pytest.mark.django_db
def test_permiso_mayorista_exige_aprobacion() -> None:
    usuario = get_user_model().objects.create_user(
        username="mayorista-pendiente@example.com",
        password="test-password",
    )
    perfil = PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.CLIENTE_MAYORISTA,
        mayorista_aprobado=False,
    )
    request_base = APIRequestFactory().get("/")
    force_authenticate(request_base, user=usuario)
    request = APIView().initialize_request(request_base)
    permiso = EsMayoristaAprobado()

    assert permiso.has_permission(request, APIView()) is False

    perfil.mayorista_aprobado = True
    perfil.save(update_fields=["mayorista_aprobado"])
    assert permiso.has_permission(request, APIView()) is True
