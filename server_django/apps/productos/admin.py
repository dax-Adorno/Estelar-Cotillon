"""Configuracion administrativa de productos."""

from django.contrib import admin

from apps.productos.models import Categoria, ImagenProducto, Producto


class ImagenProductoInline(admin.TabularInline):
    """Imagenes asociadas a un producto."""

    model = ImagenProducto
    extra = 1
    fields = (
        "imagen",
        "imagen_web",
        "imagen_thumbnail",
        "texto_alt",
        "principal",
        "orden",
        "activa",
    )
    readonly_fields = (
        "imagen_web",
        "imagen_thumbnail",
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Administracion de categorias."""

    list_display = (
        "nombre",
        "slug",
        "activa",
    )
    list_filter = ("activa",)
    search_fields = (
        "nombre",
        "slug",
    )
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Administracion de productos."""

    list_display = (
        "sku",
        "nombre",
        "categoria",
        "precio_minorista",
        "precio_mayorista",
        "stock",
        "activo",
        "destacado",
    )
    list_filter = (
        "categoria",
        "activo",
        "destacado",
    )
    search_fields = (
        "sku",
        "nombre",
        "slug",
    )
    prepopulated_fields = {"slug": ("nombre",)}
    inlines = [ImagenProductoInline]


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    """Administracion de imagenes de producto."""

    list_display = (
        "producto",
        "principal",
        "orden",
        "activa",
    )
    list_filter = (
        "principal",
        "activa",
    )
    search_fields = (
        "producto__sku",
        "producto__nombre",
        "texto_alt",
    )
