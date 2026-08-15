"""Serializers de promociones."""

from rest_framework import serializers

from apps.promociones.models import Promocion


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
