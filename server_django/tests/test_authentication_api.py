"""Pruebas del flujo de autenticacion basado en sesion."""

from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from apps.clientes.models import Cliente, PerfilUsuario


@pytest.fixture(name="api_client_csrf")
def fixture_api_client_csrf() -> APIClient:
    """Cliente que aplica las mismas comprobaciones CSRF que produccion."""
    return APIClient(enforce_csrf_checks=True)


def _obtener_csrf(api_client: APIClient) -> str:
    response = api_client.get("/api/v1/auth/csrf/")
    assert response.status_code == status.HTTP_200_OK
    return response.json()["csrfToken"]


def _payload_registro(**reemplazos: Any) -> dict[str, Any]:
    payload = {
        "nombre": "Ana",
        "apellido": "Gomez",
        "email": "ana@example.com",
        "whatsapp": "0981123456",
        "tipo_cliente": Cliente.TipoCliente.MINORISTA,
        "razon_social": "",
        "cuit": "",
        "password": "Clave-Segura-Estelart-2026!",
        "password_confirmacion": "Clave-Segura-Estelart-2026!",
    }
    payload.update(reemplazos)
    return payload


@pytest.mark.django_db
def test_registro_requiere_csrf(api_client_csrf: APIClient) -> None:
    """No permite registros cross-site sin token CSRF."""
    response = api_client_csrf.post(
        "/api/v1/auth/registro/",
        _payload_registro(),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_registro_crea_cuenta_inactiva_y_envia_verificacion(
    api_client_csrf: APIClient,
) -> None:
    """Crea las tres entidades sin habilitar login antes de verificar email."""
    csrf_token = _obtener_csrf(api_client_csrf)
    response = api_client_csrf.post(
        "/api/v1/auth/registro/",
        _payload_registro(),
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == status.HTTP_201_CREATED
    usuario = get_user_model().objects.get(username="ana@example.com")
    assert usuario.is_active is False
    assert usuario.check_password("Clave-Segura-Estelart-2026!")
    assert usuario.perfil_estelart.rol == PerfilUsuario.Rol.CLIENTE_MINORISTA
    assert usuario.perfil_estelart.cliente.email == "ana@example.com"
    assert len(mail.outbox) == 1
    assert "verificar-email" in mail.outbox[0].body


@pytest.mark.django_db
def test_mayorista_queda_pendiente_de_aprobacion(
    api_client_csrf: APIClient,
) -> None:
    """Solicitar cuenta mayorista no concede privilegios automaticamente."""
    csrf_token = _obtener_csrf(api_client_csrf)
    response = api_client_csrf.post(
        "/api/v1/auth/registro/",
        _payload_registro(
            email="mayorista@example.com",
            tipo_cliente=Cliente.TipoCliente.MAYORISTA,
            razon_social="Fiestas del Sur",
            cuit="80012345-6",
        ),
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == status.HTTP_201_CREATED
    perfil = PerfilUsuario.objects.get(usuario__username="mayorista@example.com")
    assert perfil.rol == PerfilUsuario.Rol.CLIENTE_MAYORISTA
    assert perfil.mayorista_aprobado is False


@pytest.mark.django_db
def test_verificacion_habilita_login_y_sesion(
    api_client_csrf: APIClient,
) -> None:
    """Activa email, inicia sesion, consulta identidad y cierra sesion."""
    csrf_token = _obtener_csrf(api_client_csrf)
    api_client_csrf.post(
        "/api/v1/auth/registro/",
        _payload_registro(),
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    usuario = get_user_model().objects.get(username="ana@example.com")
    uid = urlsafe_base64_encode(str(usuario.pk).encode("utf-8"))
    token = default_token_generator.make_token(usuario)

    response_verificacion = api_client_csrf.post(
        "/api/v1/auth/verificar-email/",
        {"uid": uid, "token": token},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert response_verificacion.status_code == status.HTTP_200_OK

    response_login = api_client_csrf.post(
        "/api/v1/auth/login/",
        {"email": "ANA@example.com", "password": "Clave-Segura-Estelart-2026!"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert response_login.status_code == status.HTTP_200_OK
    assert response_login.data["rol"] == PerfilUsuario.Rol.CLIENTE_MINORISTA

    response_me = api_client_csrf.get("/api/v1/auth/me/")
    assert response_me.status_code == status.HTTP_200_OK
    assert response_me.data["email"] == "ana@example.com"

    csrf_rotado = api_client_csrf.cookies["csrftoken"].value
    response_logout = api_client_csrf.post(
        "/api/v1/auth/logout/",
        format="json",
        HTTP_X_CSRFTOKEN=csrf_rotado,
    )
    assert response_logout.status_code == status.HTTP_204_NO_CONTENT
    assert api_client_csrf.get("/api/v1/auth/me/").status_code == 403


@pytest.mark.django_db
def test_login_no_revela_si_cuenta_existe(api_client_csrf: APIClient) -> None:
    """Usa un error generico ante credenciales invalidas."""
    csrf_token = _obtener_csrf(api_client_csrf)
    response = api_client_csrf.post(
        "/api/v1/auth/login/",
        {"email": "nadie@example.com", "password": "Clave-invalida-2026!"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "detalle": "Credenciales invalidas o cuenta no activada.",
    }


@pytest.mark.django_db
def test_recuperacion_no_revela_si_email_existe(
    api_client_csrf: APIClient,
) -> None:
    """Responde igual para cuentas existentes e inexistentes."""
    csrf_token = _obtener_csrf(api_client_csrf)
    respuesta_inexistente = api_client_csrf.post(
        "/api/v1/auth/password-reset/",
        {"email": "nadie@example.com"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert respuesta_inexistente.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_recuperacion_reemplaza_password(
    api_client_csrf: APIClient,
) -> None:
    """Un token valido permite cambiar la clave una sola vez."""
    usuario = get_user_model().objects.create_user(
        username="cuenta@example.com",
        email="cuenta@example.com",
        password="Clave-Anterior-Estelart-2026!",
        is_active=True,
    )
    csrf_token = _obtener_csrf(api_client_csrf)
    respuesta_solicitud = api_client_csrf.post(
        "/api/v1/auth/password-reset/",
        {"email": "cuenta@example.com"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert respuesta_solicitud.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1

    uid = urlsafe_base64_encode(str(usuario.pk).encode("utf-8"))
    token = default_token_generator.make_token(usuario)
    respuesta_confirmacion = api_client_csrf.post(
        "/api/v1/auth/password-reset-confirm/",
        {
            "uid": uid,
            "token": token,
            "password": "Clave-Nueva-Estelart-2026!",
            "password_confirmacion": "Clave-Nueva-Estelart-2026!",
        },
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert respuesta_confirmacion.status_code == status.HTTP_200_OK
    usuario.refresh_from_db()
    assert usuario.check_password("Clave-Nueva-Estelart-2026!")

    respuesta_reuso = api_client_csrf.post(
        "/api/v1/auth/password-reset-confirm/",
        {
            "uid": uid,
            "token": token,
            "password": "Otra-Clave-Estelart-2026!",
            "password_confirmacion": "Otra-Clave-Estelart-2026!",
        },
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert respuesta_reuso.status_code == status.HTTP_400_BAD_REQUEST
