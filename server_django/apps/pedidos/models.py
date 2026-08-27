"""Modelos de pedidos."""

# pylint: disable=too-many-ancestors

from decimal import Decimal

from django.conf import settings
from django.db import models


class Pedido(models.Model):
    """Pedido comercial realizado por un cliente."""

    class EstadoPedido(models.TextChoices):
        """Estados operativos de un pedido."""

        BORRADOR = "borrador", "Borrador"
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADO = "confirmado", "Confirmado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    class EstadoPago(models.TextChoices):
        """Estados de pago de un pedido."""

        PENDIENTE = "pendiente", "Pendiente"
        PARCIAL = "parcial", "Parcial"
        PAGADO = "pagado", "Pagado"
        REEMBOLSADO = "reembolsado", "Reembolsado"

    class CanalVenta(models.TextChoices):
        """Canales comerciales desde donde puede originarse un pedido."""

        WEB = "web", "Web"
        WHATSAPP = "whatsapp", "WhatsApp"
        INSTAGRAM = "instagram", "Instagram"
        MERCADO_LIBRE = "mercado_libre", "Mercado Libre"
        TIENDA_NUBE = "tienda_nube", "Tienda Nube"
        PRESENCIAL = "presencial", "Presencial"

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    codigo = models.CharField(max_length=50, unique=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoPedido.choices,
        default=EstadoPedido.BORRADOR,
    )
    estado_pago = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
    )
    canal_venta = models.CharField(
        max_length=30,
        choices=CanalVenta.choices,
        default=CanalVenta.WHATSAPP,
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notas = models.TextField(blank=True)
    promocion_aplicada = models.ForeignKey(
        "promociones.Promocion",
        on_delete=models.PROTECT,
        related_name="pedidos",
        null=True,
        blank=True,
    )
    promocion_nombre = models.CharField(max_length=160, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pedidos"
        ordering = ["-creado_en"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["estado_pago"]),
            models.Index(fields=["canal_venta"]),
        ]

    def __str__(self) -> str:
        return self.codigo

    def calcular_total(self) -> Decimal:
        """Calcula el total del pedido aplicando descuento."""

        total = self.subtotal - self.descuento

        if total < Decimal("0.00"):
            return Decimal("0.00")

        return total


class DetallePedido(models.Model):
    """Linea de detalle asociada a un pedido."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "detalle_pedidos"
        ordering = ["id"]
        verbose_name = "detalle de pedido"
        verbose_name_plural = "detalle de pedidos"
        indexes = [
            models.Index(fields=["pedido"]),
            models.Index(fields=["producto"]),
        ]

    def __str__(self) -> str:
        return f"{self.pedido.codigo} - {self.producto.nombre}"

    def calcular_subtotal(self) -> Decimal:
        """Calcula el subtotal del detalle."""

        return self.precio_unitario * self.cantidad


class EventoPedido(models.Model):
    """Registro inmutable de cambios operativos de un pedido."""

    class TipoEvento(models.TextChoices):
        """Operaciones auditables sobre pedidos."""

        ESTADO = "estado", "Cambio de estado"
        ESTADO_PAGO = "estado_pago", "Cambio de estado de pago"

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="eventos",
    )
    tipo = models.CharField(max_length=20, choices=TipoEvento.choices)
    valor_anterior = models.CharField(max_length=30)
    valor_nuevo = models.CharField(max_length=30)
    comentario = models.CharField(max_length=500, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="eventos_pedido",
        null=True,
        blank=True,
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "eventos_pedido"
        ordering = ["-creado_en", "-id"]
        verbose_name = "evento de pedido"
        verbose_name_plural = "eventos de pedido"
        indexes = [
            models.Index(fields=["pedido", "creado_en"]),
            models.Index(fields=["tipo"]),
        ]

    def __str__(self) -> str:
        return f"{self.pedido.codigo}: {self.valor_anterior} -> {self.valor_nuevo}"
