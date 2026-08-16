"""Serializers de productos."""

from typing import Any

from rest_framework import serializers

from apps.productos.models import Categoria, ImagenProducto, Producto


def construir_url_absoluta(request: Any, url: str) -> str:
    """Construye URL absoluta si existe request."""
    if request is None:
        return url

    return request.build_absolute_uri(url)


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer de categoria."""

    class Meta:
        model = Categoria
        fields = (
            "id",
            "nombre",
            "slug",
            "descripcion",
            "activa",
        )


class ImagenProductoSerializer(serializers.ModelSerializer):
    """Serializer de imagen de producto."""

    imagen_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenProducto
        fields = (
            "id",
            "imagen_url",
            "thumbnail_url",
            "texto_alt",
            "principal",
            "orden",
        )

    def get_imagen_url(self, obj: ImagenProducto) -> str:
        """Devuelve la URL publica de la imagen web."""
        request = self.context.get("request")
        archivo = obj.imagen_web or obj.imagen

        return construir_url_absoluta(request, archivo.url)

    def get_thumbnail_url(self, obj: ImagenProducto) -> str:
        """Devuelve la URL publica del thumbnail."""
        request = self.context.get("request")
        archivo = obj.imagen_thumbnail or obj.imagen_web or obj.imagen

        return construir_url_absoluta(request, archivo.url)


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de producto."""

    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True,
    )
    imagen_principal = serializers.SerializerMethodField()
    thumbnail_principal = serializers.SerializerMethodField()
    imagenes = ImagenProductoSerializer(many=True, read_only=True)

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
            "imagen_principal",
            "thumbnail_principal",
            "imagenes",
        )

    def get_imagen_principal(self, obj: Producto) -> str | None:
        """Devuelve la URL publica de la imagen principal."""
        imagen = self._obtener_imagen_principal(obj)

        if imagen is None:
            return None

        request = self.context.get("request")
        archivo = imagen.imagen_web or imagen.imagen

        return construir_url_absoluta(request, archivo.url)

    def get_thumbnail_principal(self, obj: Producto) -> str | None:
        """Devuelve la URL publica del thumbnail principal."""
        imagen = self._obtener_imagen_principal(obj)

        if imagen is None:
            return None

        request = self.context.get("request")
        archivo = imagen.imagen_thumbnail or imagen.imagen_web or imagen.imagen

        return construir_url_absoluta(request, archivo.url)

    @staticmethod
    def _obtener_imagen_principal(
        obj: Producto,
    ) -> ImagenProducto | None:
        """Obtiene la imagen principal activa del producto."""
        imagen = obj.imagenes.filter(
            activa=True,
            principal=True,
        ).first()

        if imagen is not None:
            return imagen

        return obj.imagenes.filter(activa=True).first()
