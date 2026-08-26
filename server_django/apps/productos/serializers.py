"""Serializers publicos y de gestion del catalogo."""

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils.text import slugify
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
    imagenes = serializers.SerializerMethodField()

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

    def get_imagenes(self, obj: Producto) -> Any:
        """Expone exclusivamente imagenes publicadas."""
        imagenes = self._obtener_imagenes_publicas(obj)
        return ImagenProductoSerializer(
            imagenes,
            many=True,
            context=self.context,
        ).data

    @staticmethod
    def _obtener_imagen_principal(
        obj: Producto,
    ) -> ImagenProducto | None:
        """Obtiene la imagen principal activa del producto."""
        imagenes = ProductoSerializer._obtener_imagenes_publicas(obj)
        imagen = next(
            (elemento for elemento in imagenes if elemento.principal),
            None,
        )

        if imagen is not None:
            return imagen

        return imagenes[0] if imagenes else None

    @staticmethod
    def _obtener_imagenes_publicas(obj: Producto) -> list[ImagenProducto]:
        """Reutiliza el prefetch publico y evita consultas por producto."""
        imagenes_prefetch = getattr(obj, "imagenes_publicas", None)
        if imagenes_prefetch is not None:
            return list(imagenes_prefetch)
        return list(obj.imagenes.filter(activa=True))


def _crear_slug_disponible(
    modelo: type[Categoria] | type[Producto],
    texto: str,
    instancia_id: int | None = None,
) -> str:
    """Genera un slug estable y unico para altas desde el panel."""
    longitud_maxima = modelo._meta.get_field("slug").max_length or 180
    base = slugify(texto)[:longitud_maxima] or "item"
    candidato = base
    contador = 2
    existentes = modelo.objects.all()
    if instancia_id is not None:
        existentes = existentes.exclude(pk=instancia_id)

    while existentes.filter(slug=candidato).exists():
        sufijo = f"-{contador}"
        candidato = f"{base[: longitud_maxima - len(sufijo)]}{sufijo}"
        contador += 1
    return candidato


class CategoriaGestionSerializer(serializers.ModelSerializer):
    """Alta y edicion segura de categorias internas."""

    slug = serializers.SlugField(
        max_length=140,
        allow_blank=True,
        required=False,
    )

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
        read_only_fields = ("id", "creada_en", "actualizada_en")

    def validate_nombre(self, value: str) -> str:
        """Normaliza el nombre e impide duplicados por mayusculas."""
        nombre = value.strip()
        existentes = Categoria.objects.filter(nombre__iexact=nombre)
        if self.instance is not None:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise serializers.ValidationError("Ya existe una categoria con ese nombre.")
        return nombre

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Autogenera slug al crear o cuando se envia vacio."""
        attrs = super().validate(attrs)
        if self.instance is None or "slug" in attrs:
            slug_enviado = attrs.get("slug", "").strip()
            texto = slug_enviado or attrs.get(
                "nombre",
                getattr(self.instance, "nombre", ""),
            )
            slug = slugify(texto)
            existentes = Categoria.objects.filter(slug=slug)
            if self.instance is not None:
                existentes = existentes.exclude(pk=self.instance.pk)
            if slug_enviado and existentes.exists():
                raise serializers.ValidationError(
                    {"slug": "Ya existe una categoria con ese slug."},
                )
            attrs["slug"] = _crear_slug_disponible(
                Categoria,
                texto,
                getattr(self.instance, "pk", None),
            )
        return attrs


class ProductoGestionSerializer(serializers.ModelSerializer):
    """Gestion comercial de productos, precios, stock y publicacion."""

    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True,
    )
    slug = serializers.SlugField(
        max_length=180,
        allow_blank=True,
        required=False,
    )
    cantidad_imagenes = serializers.IntegerField(
        source="imagenes.count",
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
            "cantidad_imagenes",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = (
            "id",
            "cantidad_imagenes",
            "creado_en",
            "actualizado_en",
        )

    def validate_sku(self, value: str) -> str:
        """Normaliza SKU e impide duplicados sin distinguir mayusculas."""
        sku = value.strip().upper()
        existentes = Producto.objects.filter(sku__iexact=sku)
        if self.instance is not None:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise serializers.ValidationError("Ya existe un producto con ese SKU.")
        return sku

    def validate_nombre(self, value: str) -> str:
        """Retira espacios accidentales del nombre comercial."""
        return value.strip()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida precios, minimo mayorista y slug SEO."""
        attrs = super().validate(attrs)
        precio_minorista = attrs.get(
            "precio_minorista",
            getattr(self.instance, "precio_minorista", Decimal("0")),
        )
        precio_mayorista = attrs.get(
            "precio_mayorista",
            getattr(self.instance, "precio_mayorista", Decimal("0")),
        )
        minimo = attrs.get(
            "cantidad_minima_mayorista",
            getattr(self.instance, "cantidad_minima_mayorista", 1),
        )

        errores: dict[str, str] = {}
        if precio_minorista <= Decimal("0"):
            errores["precio_minorista"] = "El precio debe ser mayor que cero."
        if precio_mayorista <= Decimal("0"):
            errores["precio_mayorista"] = "El precio debe ser mayor que cero."
        elif precio_mayorista > precio_minorista:
            errores["precio_mayorista"] = (
                "El precio mayorista no puede superar al minorista."
            )
        if minimo < 1:
            errores["cantidad_minima_mayorista"] = (
                "La cantidad minima debe ser al menos uno."
            )
        if errores:
            raise serializers.ValidationError(errores)

        if self.instance is None or "slug" in attrs:
            slug_enviado = attrs.get("slug", "").strip()
            texto = slug_enviado or attrs.get(
                "nombre",
                getattr(self.instance, "nombre", ""),
            )
            slug = slugify(texto)
            existentes = Producto.objects.filter(slug=slug)
            if self.instance is not None:
                existentes = existentes.exclude(pk=self.instance.pk)
            if slug_enviado and existentes.exists():
                raise serializers.ValidationError(
                    {"slug": "Ya existe un producto con ese slug."},
                )
            attrs["slug"] = _crear_slug_disponible(
                Producto,
                texto,
                getattr(self.instance, "pk", None),
            )
        return attrs


class ImagenProductoGestionSerializer(serializers.ModelSerializer):
    """Carga y organizacion de imagenes del catalogo."""

    imagen_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    producto_sku = serializers.CharField(source="producto.sku", read_only=True)

    class Meta:
        model = ImagenProducto
        fields = (
            "id",
            "producto",
            "producto_sku",
            "imagen",
            "imagen_url",
            "thumbnail_url",
            "texto_alt",
            "principal",
            "orden",
            "activa",
            "creada_en",
            "actualizada_en",
        )
        read_only_fields = (
            "id",
            "imagen_url",
            "thumbnail_url",
            "creada_en",
            "actualizada_en",
        )
        extra_kwargs = {"imagen": {"write_only": True, "required": False}}

    def get_imagen_url(self, obj: ImagenProducto) -> str:
        """Devuelve la version optimizada para web."""
        request = self.context.get("request")
        archivo = obj.imagen_web or obj.imagen
        return construir_url_absoluta(request, archivo.url)

    def get_thumbnail_url(self, obj: ImagenProducto) -> str:
        """Devuelve el thumbnail optimizado."""
        request = self.context.get("request")
        archivo = obj.imagen_thumbnail or obj.imagen_web or obj.imagen
        return construir_url_absoluta(request, archivo.url)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Exige archivo al crear y coherencia de publicacion."""
        attrs = super().validate(attrs)
        if self.instance is None and not attrs.get("imagen"):
            raise serializers.ValidationError({"imagen": "La imagen es obligatoria."})
        principal = attrs.get(
            "principal",
            getattr(self.instance, "principal", False),
        )
        activa = attrs.get("activa", getattr(self.instance, "activa", True))
        if principal and not activa:
            raise serializers.ValidationError(
                {"principal": "Una imagen principal debe estar activa."},
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> ImagenProducto:
        """Garantiza una sola imagen principal por producto."""
        if validated_data.get("principal"):
            ImagenProducto.objects.filter(
                producto=validated_data["producto"],
                principal=True,
            ).update(principal=False)
        return super().create(validated_data)

    @transaction.atomic
    def update(
        self,
        instance: ImagenProducto,
        validated_data: dict[str, Any],
    ) -> ImagenProducto:
        """Reordena la imagen principal de forma atomica."""
        producto = validated_data.get("producto", instance.producto)
        if validated_data.get("principal", instance.principal):
            ImagenProducto.objects.filter(
                producto=producto,
                principal=True,
            ).exclude(
                pk=instance.pk
            ).update(principal=False)
        return super().update(instance, validated_data)
