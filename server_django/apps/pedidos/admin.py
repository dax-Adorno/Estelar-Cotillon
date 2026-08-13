"""Configuracion administrativa de pedidos."""

from django.contrib import admin

from apps.pedidos.models import DetallePedido, Pedido


class DetallePedidoInline(admin.TabularInline):
    """Detalle editable dentro del pedido."""

    model = DetallePedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Administracion de pedidos."""

    list_display = (
        "codigo",
        "cliente",
        "estado",
        "estado_pago",
        "canal_venta",
        "subtotal",
        "descuento",
        "total",
        "creado_en",
    )
    list_filter = (
        "estado",
        "estado_pago",
        "canal_venta",
    )
    search_fields = (
        "codigo",
        "cliente__nombre",
        "cliente__apellido",
        "cliente__razon_social",
    )
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    """Administracion de detalles de pedidos."""

    list_display = (
        "pedido",
        "producto",
        "cantidad",
        "precio_unitario",
        "subtotal",
    )
    search_fields = (
        "pedido__codigo",
        "producto__nombre",
        "producto__sku",
    )
