"""Panel administrativo de pedidos."""

from django.contrib import admin
from django.db.models import QuerySet, Sum
from django.http import HttpRequest

from apps.pedidos.models import DetallePedido, Pedido


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
    inlines = (DetallePedidoInline,)
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
