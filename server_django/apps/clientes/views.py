"""Vistas API de clientes y autenticacion."""

# pylint: disable=too-many-ancestors

from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions as django_exceptions
from django.core.mail import send_mail
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clientes.models import Cliente, PerfilUsuario
from apps.clientes.permissions import (
    EsAdminEstelart,
    EsClienteEstelart,
    EsOperadorOAdmin,
)
from apps.clientes.serializers import (
    ClienteSerializer,
    ConfirmarRestablecerPasswordSerializer,
    InicioSesionSerializer,
    MiCuentaSerializer,
    RegistroUsuarioSerializer,
    PerfilUsuarioAdminSerializer,
    SolicitudRestablecerPasswordSerializer,
    UsuarioActualSerializer,
)
from apps.core.throttles import (
    InicioSesionAnonRateThrottle,
    RegistroAnonRateThrottle,
)

UserModel = get_user_model()


class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    """API de lectura para clientes activos."""

    serializer_class = ClienteSerializer
    permission_classes = (EsOperadorOAdmin,)
    queryset = Cliente.objects.filter(activo=True)


class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    """Administracion restringida de roles y aprobaciones comerciales."""

    http_method_names = ("get", "patch", "head", "options")
    permission_classes = (EsAdminEstelart,)
    serializer_class = PerfilUsuarioAdminSerializer
    queryset = PerfilUsuario.objects.select_related("usuario", "cliente").all()


class MiCuentaAPIView(APIView):
    """Consulta y edicion limitada de la ficha del cliente autenticado."""

    permission_classes = (EsClienteEstelart,)

    def get(self, request: Request) -> Response:
        cliente = request.user.perfil_estelart.cliente
        return Response(MiCuentaSerializer(cliente).data)

    def patch(self, request: Request) -> Response:
        cliente = request.user.perfil_estelart.cliente
        serializer = MiCuentaSerializer(
            cliente,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@require_GET
@ensure_csrf_cookie
def csrf_token_view(request: Request) -> JsonResponse:
    """Entrega un token CSRF para clientes web del mismo origen."""
    return JsonResponse({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class RegistroUsuarioAPIView(APIView):
    """Registra una cuenta inactiva y envia verificacion por email."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (RegistroAnonRateThrottle,)

    def post(self, request: Request) -> Response:
        serializer = RegistroUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        uid = urlsafe_base64_encode(str(usuario.pk).encode("utf-8"))
        token = default_token_generator.make_token(usuario)
        url_verificacion = (
            f"{settings.FRONTEND_URL.rstrip('/')}/verificar-email"
            f"?uid={uid}&token={token}"
        )
        send_mail(
            subject="Verifica tu cuenta ESTELART",
            message=(
                "Confirma tu correo para activar la cuenta ESTELART:\n\n"
                f"{url_verificacion}\n\n"
                "Si no solicitaste esta cuenta, ignora este mensaje."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
        )

        return Response(
            {
                "detalle": (
                    "Registro recibido. Revisa tu correo para activar la cuenta."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_protect, name="dispatch")
class VerificarEmailAPIView(APIView):
    """Activa una cuenta mediante un token de un solo proposito."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (RegistroAnonRateThrottle,)

    def post(self, request: Request) -> Response:
        uid = request.data.get("uid", "")
        token = request.data.get("token", "")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            usuario = UserModel.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            usuario = None

        if usuario is None or not default_token_generator.check_token(
            usuario,
            token,
        ):
            return Response(
                {"detalle": "El enlace de verificacion no es valido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not usuario.is_active:
            usuario.is_active = True
            usuario.save(update_fields=["is_active"])

        return Response({"detalle": "La cuenta fue activada correctamente."})


@method_decorator(csrf_protect, name="dispatch")
class InicioSesionAPIView(APIView):
    """Inicia una sesion Django mediante email y contrasena."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (InicioSesionAnonRateThrottle,)

    def post(self, request: Request) -> Response:
        serializer = InicioSesionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]
        usuario = authenticate(
            request=request,
            username=email,
            password=password,
        )

        if usuario is None:
            return Response(
                {"detalle": "Credenciales invalidas o cuenta no activada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, usuario)
        return Response(_datos_usuario_actual(usuario))


@method_decorator(csrf_protect, name="dispatch")
class SolicitarRestablecerPasswordAPIView(APIView):
    """Envia recuperacion sin revelar si el email esta registrado."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (InicioSesionAnonRateThrottle,)

    def post(self, request: Request) -> Response:
        serializer = SolicitudRestablecerPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        usuario = UserModel.objects.filter(
            username__iexact=email,
            is_active=True,
        ).first()

        if usuario is not None:
            uid = urlsafe_base64_encode(str(usuario.pk).encode("utf-8"))
            token = default_token_generator.make_token(usuario)
            url_recuperacion = (
                f"{settings.FRONTEND_URL.rstrip('/')}/restablecer-password"
                f"?uid={uid}&token={token}"
            )
            send_mail(
                subject="Restablece tu contrasena ESTELART",
                message=(
                    "Usa este enlace para crear una nueva contrasena:\n\n"
                    f"{url_recuperacion}\n\n"
                    "Si no hiciste la solicitud, ignora este mensaje."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
            )

        return Response(
            {
                "detalle": (
                    "Si existe una cuenta activa, enviaremos instrucciones al correo."
                ),
            },
        )


@method_decorator(csrf_protect, name="dispatch")
class ConfirmarRestablecerPasswordAPIView(APIView):
    """Valida el token y reemplaza la contrasena de la cuenta."""

    permission_classes = (permissions.AllowAny,)
    throttle_classes = (InicioSesionAnonRateThrottle,)

    def post(self, request: Request) -> Response:
        serializer = ConfirmarRestablecerPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = _obtener_usuario_por_token(
            serializer.validated_data["uid"],
            serializer.validated_data["token"],
        )
        if usuario is None or not usuario.is_active:
            return Response(
                {"detalle": "El enlace de recuperacion no es valido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nueva_password = serializer.validated_data["password"]
        try:
            validate_password(nueva_password, user=usuario)
        except django_exceptions.ValidationError as error:
            return Response(
                {"password": list(error.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.set_password(nueva_password)
        usuario.save(update_fields=["password"])
        return Response({"detalle": "La contrasena fue actualizada."})


class CerrarSesionAPIView(APIView):
    """Cierra la sesion autenticada actual."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsuarioActualAPIView(APIView):
    """Devuelve identidad y permisos basicos de la sesion."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        serializer = UsuarioActualSerializer(_datos_usuario_actual(request.user))
        return Response(serializer.data)


def _datos_usuario_actual(usuario: object) -> dict[str, object]:
    """Construye una respuesta sin exponer campos internos del usuario."""
    perfil = getattr(usuario, "perfil_estelart", None)
    if perfil is not None:
        rol = perfil.rol
        mayorista_aprobado = perfil.mayorista_aprobado
    elif getattr(usuario, "is_superuser", False):
        rol = PerfilUsuario.Rol.ADMIN
        mayorista_aprobado = True
    elif getattr(usuario, "is_staff", False):
        rol = PerfilUsuario.Rol.OPERADOR
        mayorista_aprobado = True
    else:
        rol = PerfilUsuario.Rol.CLIENTE_MINORISTA
        mayorista_aprobado = False

    return {
        "id": getattr(usuario, "pk"),
        "email": getattr(usuario, "email"),
        "nombre": getattr(usuario, "first_name"),
        "apellido": getattr(usuario, "last_name"),
        "rol": rol,
        "mayorista_aprobado": mayorista_aprobado,
    }


def _obtener_usuario_por_token(uid: str, token: str) -> Any | None:
    """Resuelve un usuario solo si el token firmado continua vigente."""
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        usuario = UserModel.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        return None

    if not default_token_generator.check_token(usuario, token):
        return None
    return usuario
