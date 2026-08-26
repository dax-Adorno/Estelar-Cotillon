"""Serializers de pedidos."""

# pylint: disable=abstract-method,too-many-locals

from decimal import Decimal
from typing import Any
from uuid import uuid4

from django.db import transaction
from rest_framework import serializers

from apps.clientes.models import Cliente
from apps.pedidos.models import DetallePedido, EventoPedido, Pedido
from apps.productos.models import Producto


class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializer de detalle de pedido."""

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


class EventoPedidoSerializer(serializers.ModelSerializer):
    """Evento operativo inmutable visible para personal interno."""

    usuario_email = serializers.EmailField(source="usuario.email", read_only=True)

    class Meta:
        model = EventoPedido
        fields = (
            "id",
            "tipo",
            "valor_anterior",
            "valor_nuevo",
            "comentario",
            "usuario_email",
            "creado_en",
        )


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer de pedido."""

    cliente_nombre = serializers.StringRelatedField(
        source="cliente",
        read_only=True,
    )
    detalles = DetallePedidoSerializer(
        many=True,
        read_only=True,
    )
    eventos = EventoPedidoSerializer(many=True, read_only=True)

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
            "eventos",
            "creado_en",
            "actualizado_en",
        )


class PedidoResumenSerializer(serializers.ModelSerializer):
    """Representacion liviana para listados operativos paginados."""

    cliente_nombre = serializers.StringRelatedField(
        source="cliente",
        read_only=True,
    )
    cliente_email = serializers.EmailField(source="cliente.email", read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)
    cantidad_unidades = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pedido
        fields = (
            "id",
            "cliente",
            "cliente_nombre",
            "cliente_email",
            "codigo",
            "estado",
            "estado_pago",
            "canal_venta",
            "total",
            "cantidad_items",
            "cantidad_unidades",
            "creado_en",
            "actualizado_en",
        )


class CambioEstadoPedidoSerializer(serializers.Serializer):
    """Entrada explicita para una transicion del flujo del pedido."""

    estado = serializers.ChoiceField(choices=Pedido.EstadoPedido.choices)
    comentario = serializers.CharField(
        allow_blank=True,
        max_length=500,
        required=False,
    )


class CambioEstadoPagoPedidoSerializer(serializers.Serializer):
    """Entrada explicita para una transicion del flujo de cobro."""

    estado_pago = serializers.ChoiceField(choices=Pedido.EstadoPago.choices)
    comentario = serializers.CharField(
        allow_blank=True,
        max_length=500,
        required=False,
    )


class PedidoPublicoItemSerializer(serializers.Serializer):
    """Item recibido desde el frontend para crear un pedido."""

    producto_id = serializers.IntegerField(min_value=1)
    cantidad = serializers.IntegerField(min_value=1, max_value=100)


class PedidoPublicoCreateSerializer(serializers.Serializer):
    """Serializer publico para crear pedidos desde el catalogo."""

    nombre_completo = serializers.CharField(max_length=180)
    email = serializers.EmailField()
    whatsapp = serializers.CharField(max_length=40)
    notas = serializers.CharField(
        allow_blank=True,
        required=False,
        max_length=1000,
    )
    items = PedidoPublicoItemSerializer(many=True)

    def validate_items(
        self,
        items: list[dict[str, int]],
    ) -> list[dict[str, int]]:
        """Valida que el pedido tenga productos activos."""
        if not items:
            raise serializers.ValidationError(
                "El pedido debe incluir al menos un producto.",
            )

        if len(items) > 50:
            raise serializers.ValidationError(
                "El pedido no puede superar 50 items diferentes.",
            )

        producto_ids = [item["producto_id"] for item in items]
        if len(producto_ids) != len(set(producto_ids)):
            raise serializers.ValidationError(
                "Cada producto debe aparecer una sola vez.",
            )
        productos_existentes = Producto.objects.filter(
            id__in=producto_ids,
            activo=True,
            categoria__activa=True,
        )

        if productos_existentes.count() != len(set(producto_ids)):
            raise serializers.ValidationError(
                "Uno o mas productos no existen o no estan activos.",
            )

        productos_por_id = {producto.pk: producto for producto in productos_existentes}
        for item in items:
            producto = productos_por_id[item["producto_id"]]
            if item["cantidad"] > producto.stock:
                raise serializers.ValidationError(
                    f"Stock insuficiente para {producto.sku}: "
                    f"disponible {producto.stock}.",
                )

        return items

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Pedido:
        """Crea cliente, pedido y detalles desde datos publicos."""
        items = validated_data["items"]
        nombre_completo = validated_data["nombre_completo"].strip()
        email = validated_data["email"].strip().lower()
        whatsapp = validated_data["whatsapp"].strip()
        notas = validated_data.get("notas", "").strip()

        cliente, _created = Cliente.objects.update_or_create(
            email=email,
            defaults={
                "nombre": nombre_completo,
                "apellido": "",
                "whatsapp": whatsapp,
                "telefono": whatsapp,
                "tipo_cliente": Cliente.TipoCliente.MINORISTA,
                "activo": True,
            },
        )

        pedido = Pedido.objects.create(
            cliente=cliente,
            codigo=self._generar_codigo_pedido(),
            estado=Pedido.EstadoPedido.PENDIENTE,
            estado_pago=Pedido.EstadoPago.PENDIENTE,
            canal_venta=Pedido.CanalVenta.WEB,
            notas=notas,
        )

        productos = Producto.objects.in_bulk(
            [item["producto_id"] for item in items],
        )

        subtotal = Decimal("0.00")

        for item in items:
            producto = productos[item["producto_id"]]
            cantidad = item["cantidad"]
            precio_unitario = producto.precio_minorista
            subtotal_item = precio_unitario * cantidad
            subtotal += subtotal_item

            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal_item,
            )

        pedido.subtotal = subtotal
        pedido.descuento = Decimal("0.00")
        pedido.total = pedido.calcular_total()
        pedido.save(
            update_fields=[
                "subtotal",
                "descuento",
                "total",
                "actualizado_en",
            ],
        )

        return pedido

    def _generar_codigo_pedido(self) -> str:
        """Genera un codigo corto de pedido."""
        return f"PED-{uuid4().hex[:10].upper()}"


class PedidoPublicoResponseSerializer(serializers.ModelSerializer):
    """Respuesta publica luego de crear un pedido."""

    cliente_nombre = serializers.StringRelatedField(
        source="cliente",
        read_only=True,
    )

    class Meta:
        model = Pedido
        fields = (
            "id",
            "codigo",
            "cliente_nombre",
            "estado",
            "estado_pago",
            "canal_venta",
            "subtotal",
            "descuento",
            "total",
            "creado_en",
        )


class DetallePedidoClienteSerializer(serializers.ModelSerializer):
    """Linea de pedido visible para el cliente propietario."""

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_sku = serializers.CharField(source="producto.sku", read_only=True)

    class Meta:
        model = DetallePedido
        fields = (
            "id",
            "producto",
            "producto_nombre",
            "producto_sku",
            "cantidad",
            "precio_unitario",
            "subtotal",
        )


class PedidoClienteSerializer(serializers.ModelSerializer):
    """Pedido sin datos internos ni referencias de otros clientes."""

    detalles = DetallePedidoClienteSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = (
            "id",
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
