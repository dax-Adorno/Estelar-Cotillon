"""Serializers de clientes y autenticacion."""

# pylint: disable=abstract-method

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import transaction
from rest_framework import serializers

from apps.clientes.models import Cliente, PerfilUsuario

UserModel = get_user_model()


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para clientes."""

    class Meta:
        model = Cliente
        fields = (
            "id",
            "nombre",
            "apellido",
            "razon_social",
            "tipo_cliente",
            "email",
            "telefono",
            "whatsapp",
            "documento",
            "cuit",
            "direccion",
            "ciudad",
            "provincia",
            "notas",
            "activo",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
        )


class RegistroUsuarioSerializer(serializers.Serializer):
    """Valida y crea una cuenta pendiente de verificacion por email."""

    nombre = serializers.CharField(max_length=160)
    apellido = serializers.CharField(max_length=160, allow_blank=True)
    email = serializers.EmailField(max_length=254)
    whatsapp = serializers.CharField(max_length=40, allow_blank=True)
    tipo_cliente = serializers.ChoiceField(choices=Cliente.TipoCliente.choices)
    razon_social = serializers.CharField(
        max_length=180,
        allow_blank=True,
        required=False,
    )
    cuit = serializers.CharField(
        max_length=40,
        allow_blank=True,
        required=False,
    )
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirmacion = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_email(self, value: str) -> str:
        """Normaliza email e impide cuentas o clientes ambiguos."""
        email = value.strip().lower()
        if UserModel.objects.filter(username__iexact=email).exists():
            raise serializers.ValidationError(
                "No se puede registrar una cuenta con estos datos.",
            )
        if Cliente.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "No se puede registrar una cuenta con estos datos.",
            )
        return email

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Comprueba confirmacion, fortaleza y datos mayoristas."""
        password = attrs["password"]
        if password != attrs["password_confirmacion"]:
            raise serializers.ValidationError(
                {"password_confirmacion": "Las contrasenas no coinciden."},
            )

        if attrs["tipo_cliente"] == Cliente.TipoCliente.MAYORISTA:
            if not attrs.get("razon_social", "").strip():
                raise serializers.ValidationError(
                    {"razon_social": "La razon social es obligatoria."},
                )
            if not attrs.get("cuit", "").strip():
                raise serializers.ValidationError(
                    {"cuit": "El identificador fiscal es obligatorio."},
                )

        try:
            validate_password(password)
        except django_exceptions.ValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)},
            ) from error

        return attrs

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Any:
        """Crea usuario inactivo, cliente y perfil de forma atomica."""
        validated_data.pop("password_confirmacion")
        password = validated_data.pop("password")
        tipo_cliente = validated_data.pop("tipo_cliente")
        email = validated_data.pop("email")

        cliente = Cliente.objects.create(
            email=email,
            tipo_cliente=tipo_cliente,
            activo=True,
            **validated_data,
        )
        usuario = UserModel.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=cliente.nombre,
            last_name=cliente.apellido,
            is_active=False,
        )
        rol = (
            PerfilUsuario.Rol.CLIENTE_MAYORISTA
            if tipo_cliente == Cliente.TipoCliente.MAYORISTA
            else PerfilUsuario.Rol.CLIENTE_MINORISTA
        )
        PerfilUsuario.objects.create(
            usuario=usuario,
            cliente=cliente,
            rol=rol,
            mayorista_aprobado=False,
        )
        return usuario


class InicioSesionSerializer(serializers.Serializer):
    """Credenciales para iniciar sesion."""

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class SolicitudRestablecerPasswordSerializer(serializers.Serializer):
    """Solicitud generica de recuperacion de contrasena."""

    email = serializers.EmailField(max_length=254)


class ConfirmarRestablecerPasswordSerializer(serializers.Serializer):
    """Token y nueva contrasena para completar la recuperacion."""

    uid = serializers.CharField(max_length=128)
    token = serializers.CharField(max_length=256)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirmacion = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password"] != attrs["password_confirmacion"]:
            raise serializers.ValidationError(
                {"password_confirmacion": "Las contrasenas no coinciden."},
            )
        return attrs


class UsuarioActualSerializer(serializers.Serializer):
    """Representacion segura de la cuenta autenticada."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    apellido = serializers.CharField(read_only=True)
    rol = serializers.CharField(read_only=True)
    mayorista_aprobado = serializers.BooleanField(read_only=True)
