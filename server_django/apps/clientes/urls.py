"""Rutas API de clientes."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.clientes.views import (
    CerrarSesionAPIView,
    ClienteViewSet,
    ConfirmarRestablecerPasswordAPIView,
    InicioSesionAPIView,
    RegistroUsuarioAPIView,
    PerfilUsuarioViewSet,
    SolicitarRestablecerPasswordAPIView,
    UsuarioActualAPIView,
    VerificarEmailAPIView,
    csrf_token_view,
)

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="clientes")
router.register(
    "perfiles-usuario",
    PerfilUsuarioViewSet,
    basename="perfiles-usuario",
)

urlpatterns = [
    path("auth/csrf/", csrf_token_view, name="auth-csrf"),
    path(
        "auth/registro/",
        RegistroUsuarioAPIView.as_view(),
        name="auth-registro",
    ),
    path(
        "auth/verificar-email/",
        VerificarEmailAPIView.as_view(),
        name="auth-verificar-email",
    ),
    path(
        "auth/login/",
        InicioSesionAPIView.as_view(),
        name="auth-login",
    ),
    path(
        "auth/password-reset/",
        SolicitarRestablecerPasswordAPIView.as_view(),
        name="auth-password-reset",
    ),
    path(
        "auth/password-reset-confirm/",
        ConfirmarRestablecerPasswordAPIView.as_view(),
        name="auth-password-reset-confirm",
    ),
    path(
        "auth/logout/",
        CerrarSesionAPIView.as_view(),
        name="auth-logout",
    ),
    path(
        "auth/me/",
        UsuarioActualAPIView.as_view(),
        name="auth-me",
    ),
    path("", include(router.urls)),
]
