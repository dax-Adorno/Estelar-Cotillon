"""Serializers de pedidos."""

from rest_framework import serializers

from apps.pedidos.models import DetallePedido, Pedido


class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializer para detalles de pedido."""

    producto_nombre = serializers.CharField(
        source="producto.nombre",
        read_only=True,
    )
    producto_sku = serializers.CharField(
        source="producto.sku",
        read_only=True,
    )

    class Meta:
        model = DetallePedido
        fields = (
            "id",
            "pedido",
            "producto",
            "producto_nombre",
            "producto_sku",
            "cantidad",
            "precio_unitario",
            "subtotal",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
        )


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer para pedidos."""

    cliente_nombre = serializers.StringRelatedField(
        source="cliente",
        read_only=True,
    )
    detalles = DetallePedidoSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Pedido
        fields = (
            "id",
            "cliente",
            "cliente_nombre",
            "codigo",
            "estado",
            "estado_pago",
            "canal_venta",
            "subtotal",
            "descuento",
            "total",
            "notas",
            "detalles",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
        )
