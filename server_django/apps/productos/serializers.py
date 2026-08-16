"""Serializers de productos."""

from rest_framework import serializers

from apps.productos.models import Categoria, ImagenProducto, Producto


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

    class Meta:
        model = ImagenProducto
        fields = (
            "id",
            "imagen_url",
            "texto_alt",
            "principal",
            "orden",
        )

    def get_imagen_url(self, obj: ImagenProducto) -> str:
        """Devuelve la URL publica de la imagen."""
        request = self.context.get("request")

        if request is None:
            return obj.imagen.url

        return request.build_absolute_uri(obj.imagen.url)


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de producto."""

    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True,
    )
    imagen_principal = serializers.SerializerMethodField()
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
            "imagenes",
        )

    def get_imagen_principal(self, obj: Producto) -> str | None:
        """Devuelve la URL publica de la imagen principal."""
        imagen = obj.imagenes.filter(activa=True, principal=True).first()

        if imagen is None:
            imagen = obj.imagenes.filter(activa=True).first()

        if imagen is None:
            return None

        request = self.context.get("request")

        if request is None:
            return imagen.imagen.url

        return request.build_absolute_uri(imagen.imagen.url)
