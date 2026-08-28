"""Comprobaciones adicionales para impedir despliegues inseguros."""

from urllib.parse import urlparse

from django.conf import settings
from django.core.checks import Error, Tags, register


def _uses_https(value: str) -> bool:
    return urlparse(value).scheme == "https"


@register(Tags.security, deploy=True)
def production_configuration_check(app_configs, **kwargs):
    del app_configs, kwargs
    if settings.DEBUG:
        return []

    errors = []
    unsafe_secret_markers = ("unsafe", "change-me", "replace-with")
    secret_key = settings.SECRET_KEY.lower()
    if len(settings.SECRET_KEY) < 50 or any(
        marker in secret_key for marker in unsafe_secret_markers
    ):
        errors.append(
            Error(
                "DJANGO_SECRET_KEY debe ser aleatoria y tener al menos 50 caracteres.",
                id="estelart.E001",
            )
        )

    if not settings.ALLOWED_HOSTS or "*" in settings.ALLOWED_HOSTS:
        errors.append(
            Error(
                "DJANGO_ALLOWED_HOSTS debe enumerar los dominios de producción.",
                id="estelart.E002",
            )
        )

    secure_urls = [settings.FRONTEND_URL]
    secure_urls.extend(settings.CORS_ALLOWED_ORIGINS)
    secure_urls.extend(settings.CSRF_TRUSTED_ORIGINS)
    if any(not _uses_https(url) for url in secure_urls):
        errors.append(
            Error(
                "Frontend, CORS y CSRF deben utilizar HTTPS en producción.",
                id="estelart.E003",
            )
        )

    if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
        errors.append(
            Error(
                "Producción debe utilizar PostgreSQL.",
                id="estelart.E004",
            )
        )

    return errors
