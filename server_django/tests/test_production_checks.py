from unittest.mock import patch

from django.conf import settings
from django.test import override_settings

from apps.core.checks import production_configuration_check

SECURE_DATABASE = {"default": {"ENGINE": "django.db.backends.postgresql"}}


@override_settings(
    DEBUG=False,
    SECRET_KEY="a-secure-production-secret-key-with-more-than-fifty-characters-123",
    ALLOWED_HOSTS=["tienda.example.com"],
    FRONTEND_URL="https://tienda.example.com",
    CORS_ALLOWED_ORIGINS=["https://tienda.example.com"],
    CSRF_TRUSTED_ORIGINS=["https://tienda.example.com"],
)
def test_production_check_deberia_aceptar_configuracion_segura():
    with patch.object(settings, "DATABASES", SECURE_DATABASE):
        assert not production_configuration_check(None)


@override_settings(
    DEBUG=False,
    SECRET_KEY="unsafe-dev-secret-key",
    ALLOWED_HOSTS=["*"],
    FRONTEND_URL="http://tienda.example.com",
    CORS_ALLOWED_ORIGINS=["http://tienda.example.com"],
    CSRF_TRUSTED_ORIGINS=["http://tienda.example.com"],
)
def test_production_check_deberia_detectar_configuracion_insegura():
    insecure_database = {"default": {"ENGINE": "django.db.backends.sqlite3"}}
    with patch.object(settings, "DATABASES", insecure_database):
        errors = production_configuration_check(None)

    assert {error.id for error in errors} == {
        "estelart.E001",
        "estelart.E002",
        "estelart.E003",
        "estelart.E004",
    }
