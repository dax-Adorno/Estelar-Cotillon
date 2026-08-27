"""Configuracion administrativa de promociones."""

from django.contrib import admin

from apps.promociones.models import ItemComboPromocion, Promocion


class ItemComboPromocionInline(admin.TabularInline):
    """Productos y cantidades requeridos para combos."""

    model = ItemComboPromocion
    extra = 1


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    """Administracion de promociones."""

    list_display = (
        "nombre",
        "tipo_promocion",
        "canal_venta",
        "activa",
        "fecha_inicio",
        "fecha_fin",
    )
    list_filter = (
        "tipo_promocion",
        "canal_venta",
        "activa",
    )
    search_fields = (
        "nombre",
        "slug",
        "descripcion",
    )
    prepopulated_fields = {"slug": ("nombre",)}
    filter_horizontal = (
        "productos",
        "categorias",
    )
    inlines = (ItemComboPromocionInline,)
