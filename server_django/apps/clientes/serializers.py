"""Serializers de clientes."""

from rest_framework import serializers

from apps.clientes.models import Cliente


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
