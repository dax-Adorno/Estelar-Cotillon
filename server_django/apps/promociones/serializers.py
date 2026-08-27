"""Serializers publicos y de gestion de promociones."""

from typing import Any

from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers

from apps.promociones.models import ItemComboPromocion, Promocion


class ItemComboPromocionSerializer(serializers.ModelSerializer):
    """Componente publico de un combo."""

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_sku = serializers.CharField(source="producto.sku", read_only=True)

    class Meta:
        model = ItemComboPromocion
        fields = (
            "id",
            "producto",
            "producto_nombre",
            "producto_sku",
            "cantidad",
        )
        read_only_fields = fields


class PromocionSerializer(serializers.ModelSerializer):
    """Serializer para promociones."""

    productos_nombres = serializers.StringRelatedField(
        source="productos",
        many=True,
        read_only=True,
    )
    categorias_nombres = serializers.StringRelatedField(
        source="categorias",
        many=True,
        read_only=True,
    )
    vigente = serializers.SerializerMethodField()
    items_combo = ItemComboPromocionSerializer(many=True, read_only=True)

    class Meta:
        model = Promocion
        fields = (
            "id",
            "nombre",
            "slug",
            "descripcion",
            "tipo_promocion",
            "porcentaje_descuento",
            "monto_descuento",
            "compra_minima",
            "canal_venta",
            "productos",
            "productos_nombres",
            "categorias",
            "categorias_nombres",
            "items_combo",
            "fecha_inicio",
            "fecha_fin",
            "activa",
            "vigente",
            "creada_en",
            "actualizada_en",
        )
        read_only_fields = (
            "id",
            "vigente",
            "creada_en",
            "actualizada_en",
        )

    def get_vigente(self, obj: Promocion) -> bool:
        """Devuelve si la promocion esta vigente."""

        return obj.esta_vigente()


class ItemComboPromocionGestionSerializer(serializers.ModelSerializer):
    """Entrada para definir productos y cantidades de un combo."""

    cantidad = serializers.IntegerField(min_value=1, max_value=1000)
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_sku = serializers.CharField(source="producto.sku", read_only=True)

    class Meta:
        model = ItemComboPromocion
        fields = (
            "id",
            "producto",
            "producto_nombre",
            "producto_sku",
            "cantidad",
        )
        read_only_fields = ("id", "producto_nombre", "producto_sku")


def _slug_promocion_disponible(
    texto: str,
    instancia_id: int | None = None,
) -> str:
    """Genera slug unico para altas desde la gestion interna."""
    longitud_maxima = 180
    base = slugify(texto)[:longitud_maxima] or "promocion"
    candidato = base
    contador = 2
    existentes = Promocion.objects.all()
    if instancia_id is not None:
        existentes = existentes.exclude(pk=instancia_id)
    while existentes.filter(slug=candidato).exists():
        sufijo = f"-{contador}"
        candidato = f"{base[: longitud_maxima - len(sufijo)]}{sufijo}"
        contador += 1
    return candidato


class PromocionGestionSerializer(serializers.ModelSerializer):
    """Gestion validada de beneficios, alcance, vigencia y combos."""

    slug = serializers.SlugField(
        max_length=180,
        allow_blank=True,
        required=False,
    )
    productos_nombres = serializers.StringRelatedField(
        source="productos",
        many=True,
        read_only=True,
    )
    categorias_nombres = serializers.StringRelatedField(
        source="categorias",
        many=True,
        read_only=True,
    )
    items_combo = ItemComboPromocionGestionSerializer(
        many=True,
        required=False,
    )
    vigente = serializers.SerializerMethodField()

    class Meta:
        model = Promocion
        fields = (
            "id",
            "nombre",
            "slug",
            "descripcion",
            "tipo_promocion",
            "porcentaje_descuento",
            "monto_descuento",
            "compra_minima",
            "canal_venta",
            "productos",
            "productos_nombres",
            "categorias",
            "categorias_nombres",
            "items_combo",
            "fecha_inicio",
            "fecha_fin",
            "activa",
            "vigente",
            "creada_en",
            "actualizada_en",
        )
        read_only_fields = (
            "id",
            "vigente",
            "creada_en",
            "actualizada_en",
        )

    def get_vigente(self, obj: Promocion) -> bool:
        return obj.esta_vigente()

    def validate_nombre(self, value: str) -> str:
        return value.strip()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Exige fechas, descuento y composicion coherentes con el tipo."""
        attrs = super().validate(attrs)
        tipo = attrs.get(
            "tipo_promocion",
            getattr(
                self.instance, "tipo_promocion", Promocion.TipoPromocion.PORCENTAJE
            ),
        )
        errores: dict[str, str] = {}
        self._validar_fechas(attrs, errores)
        self._validar_descuento(tipo, attrs, errores)
        self._validar_items_combo(tipo, attrs, errores)
        if errores:
            raise serializers.ValidationError(errores)
        self._preparar_slug(attrs)
        return attrs

    def _validar_fechas(
        self,
        attrs: dict[str, Any],
        errores: dict[str, str],
    ) -> None:
        inicio = attrs.get("fecha_inicio", getattr(self.instance, "fecha_inicio", None))
        fin = attrs.get("fecha_fin", getattr(self.instance, "fecha_fin", None))
        if inicio is not None and fin is not None and fin <= inicio:
            errores["fecha_fin"] = "La fecha final debe ser posterior al inicio."

    def _validar_descuento(
        self,
        tipo: str,
        attrs: dict[str, Any],
        errores: dict[str, str],
    ) -> None:
        porcentaje = attrs.get(
            "porcentaje_descuento",
            getattr(self.instance, "porcentaje_descuento", None),
        )
        monto = attrs.get(
            "monto_descuento",
            getattr(self.instance, "monto_descuento", None),
        )
        if tipo == Promocion.TipoPromocion.ENVIO_GRATIS:
            if porcentaje is not None or monto is not None:
                errores["tipo_promocion"] = (
                    "El envio gratis no debe definir descuento monetario."
                )
        elif (porcentaje is None) == (monto is None):
            errores["porcentaje_descuento"] = (
                "Defina exactamente un porcentaje o un monto de descuento."
            )
        elif tipo == Promocion.TipoPromocion.PORCENTAJE and porcentaje is None:
            errores["porcentaje_descuento"] = "Esta promocion requiere un porcentaje."
        elif tipo == Promocion.TipoPromocion.MONTO_FIJO and monto is None:
            errores["monto_descuento"] = "Esta promocion requiere un monto fijo."
        elif porcentaje is not None and porcentaje <= 0:
            errores["porcentaje_descuento"] = "El porcentaje debe ser mayor que cero."
        elif monto is not None and monto <= 0:
            errores["monto_descuento"] = "El monto debe ser mayor que cero."

    def _validar_items_combo(
        self,
        tipo: str,
        attrs: dict[str, Any],
        errores: dict[str, str],
    ) -> None:
        items_enviados = attrs.get("items_combo")
        if tipo == Promocion.TipoPromocion.COMBO:
            if items_enviados is None:
                tiene_items = bool(self.instance and self.instance.items_combo.exists())
            else:
                producto_ids = [item["producto"].pk for item in items_enviados]
                tiene_items = bool(producto_ids)
                if len(producto_ids) != len(set(producto_ids)):
                    errores["items_combo"] = (
                        "Cada producto puede aparecer una sola vez en el combo."
                    )
            if not tiene_items:
                errores["items_combo"] = "Un combo debe incluir al menos un producto."
        elif items_enviados:
            errores["items_combo"] = "Solo las promociones combo admiten items."

    def _preparar_slug(self, attrs: dict[str, Any]) -> None:
        if self.instance is None or "slug" in attrs:
            slug_enviado = attrs.get("slug", "").strip()
            texto = slug_enviado or attrs.get(
                "nombre",
                getattr(self.instance, "nombre", ""),
            )
            slug = slugify(texto)
            existentes = Promocion.objects.filter(slug=slug)
            if self.instance is not None:
                existentes = existentes.exclude(pk=self.instance.pk)
            if slug_enviado and existentes.exists():
                raise serializers.ValidationError(
                    {"slug": "Ya existe una promocion con ese slug."},
                )
            attrs["slug"] = _slug_promocion_disponible(
                texto,
                getattr(self.instance, "pk", None),
            )

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Promocion:
        items = validated_data.pop("items_combo", [])
        promocion = super().create(validated_data)
        self._sincronizar_items(promocion, items)
        return promocion

    @transaction.atomic
    def update(
        self,
        instance: Promocion,
        validated_data: dict[str, Any],
    ) -> Promocion:
        items = validated_data.pop("items_combo", None)
        promocion = super().update(instance, validated_data)
        if promocion.tipo_promocion != Promocion.TipoPromocion.COMBO:
            promocion.items_combo.all().delete()
        elif items is not None:
            self._sincronizar_items(promocion, items)
        return promocion

    @staticmethod
    def _sincronizar_items(
        promocion: Promocion,
        items: list[dict[str, Any]],
    ) -> None:
        promocion.items_combo.all().delete()
        ItemComboPromocion.objects.bulk_create(
            [
                ItemComboPromocion(
                    promocion=promocion,
                    producto=item["producto"],
                    cantidad=item["cantidad"],
                )
                for item in items
            ],
        )
        if promocion.tipo_promocion == Promocion.TipoPromocion.COMBO:
            promocion.productos.set(item["producto"] for item in items)
