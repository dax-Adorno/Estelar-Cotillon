"""Serializers de productos."""

from rest_framework import serializers

from apps.productos.models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para categorias del catalogo."""

    class Meta:
        model = Categoria
        fields = (
            "id",
            "nombre",
            "slug",
            "descripcion",
            "activa",
            "creada_en",
            "actualizada_en",
        )
        read_only_fields = (
            "id",
            "creada_en",
            "actualizada_en",
        )


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer para productos del catalogo."""

    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True,
    )

    class Meta:
        model = Producto
        fields = (
            "id",
            "categoria",
            "categoria_nombre",
            "sku",
            "nombre",
            "slug",
            "descripcion",
            "precio_minorista",
            "precio_mayorista",
            "cantidad_minima_mayorista",
            "stock",
            "activo",
            "destacado",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "creado_en",
            "actualizado_en",
        )
