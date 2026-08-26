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


class PerfilUsuarioAdminSerializer(serializers.ModelSerializer):
    """Gestion administrativa segura de roles y aprobaciones."""

    email = serializers.EmailField(source="usuario.email", read_only=True)
    nombre = serializers.CharField(source="usuario.first_name", read_only=True)
    apellido = serializers.CharField(source="usuario.last_name", read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = (
            "id",
            "usuario",
            "email",
            "nombre",
            "apellido",
            "cliente",
            "rol",
            "mayorista_aprobado",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "usuario",
            "cliente",
            "creado_en",
            "actualizado_en",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Evita escalamiento indebido y estados comerciales incoherentes."""
        request = self.context.get("request")
        nuevo_rol = attrs.get("rol", self.instance.rol)
        aprobado = attrs.get(
            "mayorista_aprobado",
            self.instance.mayorista_aprobado,
        )

        if (
            nuevo_rol == PerfilUsuario.Rol.ADMIN
            and request is not None
            and not request.user.is_superuser
        ):
            raise serializers.ValidationError(
                {"rol": "Solo un superusuario puede asignar administradores."},
            )
        if (
            request is not None
            and self.instance.usuario_id == request.user.pk
            and self.instance.rol == PerfilUsuario.Rol.ADMIN
            and nuevo_rol != PerfilUsuario.Rol.ADMIN
        ):
            raise serializers.ValidationError(
                {"rol": "No puedes quitar tu propio rol de administrador."},
            )
        if aprobado and nuevo_rol != PerfilUsuario.Rol.CLIENTE_MAYORISTA:
            raise serializers.ValidationError(
                {
                    "mayorista_aprobado": (
                        "Solo una cuenta mayorista puede recibir esta aprobacion."
                    ),
                },
            )
        return attrs

    @transaction.atomic
    def update(
        self,
        instance: PerfilUsuario,
        validated_data: dict[str, Any],
    ) -> PerfilUsuario:
        """Actualiza el perfil y sincroniza permisos nativos y tipo de cliente."""
        perfil = super().update(instance, validated_data)
        usuario = perfil.usuario
        usuario.is_staff = perfil.rol in {
            PerfilUsuario.Rol.OPERADOR,
            PerfilUsuario.Rol.ADMIN,
        }
        usuario.save(update_fields=["is_staff"])

        if perfil.cliente is not None:
            if perfil.rol == PerfilUsuario.Rol.CLIENTE_MAYORISTA:
                perfil.cliente.tipo_cliente = Cliente.TipoCliente.MAYORISTA
            elif perfil.rol == PerfilUsuario.Rol.CLIENTE_MINORISTA:
                perfil.cliente.tipo_cliente = Cliente.TipoCliente.MINORISTA
            perfil.cliente.save(update_fields=["tipo_cliente", "actualizado_en"])
        return perfil


class MiCuentaSerializer(serializers.ModelSerializer):
    """Datos comerciales que el cliente puede consultar y actualizar."""

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
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "tipo_cliente",
            "email",
            "creado_en",
            "actualizado_en",
        )

    @transaction.atomic
    def update(
        self,
        instance: Cliente,
        validated_data: dict[str, Any],
    ) -> Cliente:
        """Mantiene nombre y apellido sincronizados con la cuenta Django."""
        cliente = super().update(instance, validated_data)
        perfil = getattr(cliente, "perfil_usuario", None)
        if perfil is not None:
            usuario = perfil.usuario
            usuario.first_name = cliente.nombre
            usuario.last_name = cliente.apellido
            usuario.save(update_fields=["first_name", "last_name"])
        return cliente
