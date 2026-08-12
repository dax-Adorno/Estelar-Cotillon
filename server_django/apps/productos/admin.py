"""Configuracion administrativa de productos."""

from django.contrib import admin

from apps.productos.models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Administracion de categorias."""

    list_display = (
        "nombre",
        "slug",
        "activa",
        "creada_en",
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
