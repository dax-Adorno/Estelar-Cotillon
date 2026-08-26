"""Panel administrativo de pedidos."""

from collections.abc import (
    Callable,
)

from django.contrib import admin, messages
from django.db.models import QuerySet, Sum
from django.http import HttpRequest

from apps.pedidos.models import DetallePedido, EventoPedido, Pedido
from apps.pedidos.services import (
    TransicionPedidoError,
    cambiar_estado_pago_pedido,
    cambiar_estado_pedido,
)


class DetallePedidoInline(admin.TabularInline):
    """Detalle de productos dentro del pedido."""

    model = DetallePedido
    fields = (
        "producto",
        "cantidad",
        "precio_unitario",
        "subtotal",
    )
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(
        self,
        request: HttpRequest,
        obj: Pedido | None = None,
    ) -> bool:
        """Evita agregar detalles manualmente desde el inline."""
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Pedido | None = None,
    ) -> bool:
        """Evita borrar detalles manualmente desde el inline."""
        return False


class EventoPedidoInline(admin.TabularInline):
    """Historial inmutable de transiciones del pedido."""

    model = EventoPedido
    fields = (
        "tipo",
        "valor_anterior",
        "valor_nuevo",
        "comentario",
        "usuario",
        "creado_en",
    )
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(
        self,
        request: HttpRequest,
        obj: Pedido | None = None,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Pedido | None = None,
    ) -> bool:
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Panel operativo para seguimiento de pedidos."""

    list_display = (
        "codigo",
        "cliente",
        "estado",
        "estado_pago",
        "canal_venta",
        "cantidad_items",
        "cantidad_unidades",
        "total",
        "creado_en",
    )
    list_filter = (
        "estado",
        "estado_pago",
        "canal_venta",
        "creado_en",
    )
    search_fields = (
        "codigo",
        "cliente__nombre",
        "cliente__apellido",
        "cliente__razon_social",
        "cliente__email",
        "cliente__whatsapp",
    )
    readonly_fields = (
        "codigo",
        "estado",
        "estado_pago",
        "subtotal",
        "descuento",
        "total",
        "creado_en",
        "actualizado_en",
    )
    fieldsets = (
        (
            "Datos principales",
            {
                "fields": (
                    "codigo",
                    "cliente",
                    "estado",
                    "estado_pago",
                    "canal_venta",
                ),
            },
        ),
        (
            "Importes",
            {
                "fields": (
                    "subtotal",
                    "descuento",
                    "total",
                ),
            },
        ),
        (
            "Notas",
            {
                "fields": ("notas",),
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "creado_en",
                    "actualizado_en",
                ),
            },
        ),
    )
    inlines = (DetallePedidoInline, EventoPedidoInline)
    actions = (
        "marcar_pendientes",
        "confirmar_pedidos",
        "marcar_entregados",
        "cancelar_pedidos",
        "marcar_pago_parcial",
        "marcar_pagados",
        "marcar_reembolsados",
    )
    date_hierarchy = "creado_en"
    ordering = ("-creado_en",)
    list_select_related = ("cliente",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Pedido]:
        """Optimiza consultas del panel operativo."""
        queryset = super().get_queryset(request)

        return queryset.select_related("cliente").prefetch_related(
            "detalles__producto",
        )

    @admin.display(description="Ítems")
    def cantidad_items(self, obj: Pedido) -> int:
        """Cantidad de líneas de detalle del pedido."""
        return obj.detalles.count()

    @admin.display(description="Unidades")
    def cantidad_unidades(self, obj: Pedido) -> int:
        """Cantidad total de unidades del pedido."""
        total = obj.detalles.aggregate(
            total_unidades=Sum("cantidad"),
        )["total_unidades"]

        return int(total or 0)

    @admin.action(description="Mover a pendiente")
    def marcar_pendientes(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
    ) -> None:
        self._aplicar_transicion(
            request,
            queryset,
            cambiar_estado_pedido,
            Pedido.EstadoPedido.PENDIENTE,
        )

    @admin.action(description="Confirmar y reservar stock")
    def confirmar_pedidos(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
    ) -> None:
        self._aplicar_transicion(
            request,
            queryset,
            cambiar_estado_pedido,
            Pedido.EstadoPedido.CONFIRMADO,
        )

    @admin.action(description="Marcar como entregados")
    def marcar_entregados(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
    ) -> None:
        self._aplicar_transicion(
            request,
            queryset,
            cambiar_estado_pedido,
            Pedido.EstadoPedido.ENTREGADO,
        )

    @admin.action(description="Cancelar y liberar stock reservado")
    def cancelar_pedidos(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
    ) -> None:
        self._aplicar_transicion(
            request,
            queryset,
            cambiar_estado_pedido,
            Pedido.EstadoPedido.CANCELADO,
        )

    @admin.action(description="Registrar pago parcial")
    def marcar_pago_parcial(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
    ) -> None:
        self._aplicar_transicion(
            request,
            queryset,
            cambiar_estado_pago_pedido,
            Pedido.EstadoPago.PARCIAL,
        )

    @admin.action(description="Marcar como pagados")
    def marcar_pagados(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
    ) -> None:
        self._aplicar_transicion(
            request,
            queryset,
            cambiar_estado_pago_pedido,
            Pedido.EstadoPago.PAGADO,
        )

    @admin.action(description="Registrar reembolso")
    def marcar_reembolsados(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
    ) -> None:
        self._aplicar_transicion(
            request,
            queryset,
            cambiar_estado_pago_pedido,
            Pedido.EstadoPago.REEMBOLSADO,
        )

    def _aplicar_transicion(
        self,
        request: HttpRequest,
        queryset: QuerySet[Pedido],
        servicio: Callable[..., Pedido],
        destino: str,
    ) -> None:
        """Ejecuta acciones masivas usando las reglas del dominio."""
        exitos = 0
        errores: list[str] = []
        for pedido in queryset:
            try:
                servicio(
                    pedido_id=pedido.pk,
                    nuevo_estado=destino,
                    usuario=request.user,
                    comentario="Cambio realizado desde Django Admin.",
                )
                exitos += 1
            except TransicionPedidoError as error:
                errores.append(f"{pedido.codigo}: {error}")

        if exitos:
            self.message_user(
                request,
                f"Pedidos actualizados correctamente: {exitos}.",
                level=messages.SUCCESS,
            )
        if errores:
            self.message_user(
                request,
                " | ".join(errores),
                level=messages.ERROR,
            )


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    """Panel administrativo de detalles de pedido."""

    list_display = (
        "pedido",
        "producto",
        "cantidad",
        "precio_unitario",
        "subtotal",
        "creado_en",
    )
    list_filter = ("creado_en",)
    search_fields = (
        "pedido__codigo",
        "producto__nombre",
        "producto__sku",
    )
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )
    ordering = ("-creado_en",)
    list_select_related = (
        "pedido",
        "producto",
    )


@admin.register(EventoPedido)
class EventoPedidoAdmin(admin.ModelAdmin):
    """Consulta central del historial operativo."""

    list_display = (
        "pedido",
        "tipo",
        "valor_anterior",
        "valor_nuevo",
        "usuario",
        "creado_en",
    )
    list_filter = ("tipo", "creado_en")
    search_fields = ("pedido__codigo", "usuario__email", "comentario")
    readonly_fields = (
        "pedido",
        "tipo",
        "valor_anterior",
        "valor_nuevo",
        "comentario",
        "usuario",
        "creado_en",
    )
    ordering = ("-creado_en",)
    list_select_related = ("pedido", "usuario")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: EventoPedido | None = None,
    ) -> bool:
        return False
