"""Modelos de promociones."""

# pylint: disable=too-many-ancestors

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Promocion(models.Model):
    """Promocion comercial aplicable a productos o categorias."""

    class TipoPromocion(models.TextChoices):
        """Tipos de promociones comerciales."""

        PORCENTAJE = "porcentaje", "Porcentaje"
        MONTO_FIJO = "monto_fijo", "Monto fijo"
        COMBO = "combo", "Combo"
        MAYORISTA = "mayorista", "Mayorista"
        TEMPORADA = "temporada", "Temporada"
        ENVIO_GRATIS = "envio_gratis", "Envio gratis"

    class CanalVenta(models.TextChoices):
        """Canales donde aplica la promocion."""

        TODOS = "todos", "Todos"
        WEB = "web", "Web"
        WHATSAPP = "whatsapp", "WhatsApp"
        INSTAGRAM = "instagram", "Instagram"
        MERCADO_LIBRE = "mercado_libre", "Mercado Libre"
        TIENDA_NUBE = "tienda_nube", "Tienda Nube"
        PRESENCIAL = "presencial", "Presencial"

    nombre = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    descripcion = models.TextField(blank=True)
    tipo_promocion = models.CharField(
        max_length=30,
        choices=TipoPromocion.choices,
        default=TipoPromocion.PORCENTAJE,
    )
    porcentaje_descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )
    monto_descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    compra_minima = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    canal_venta = models.CharField(
        max_length=30,
        choices=CanalVenta.choices,
        default=CanalVenta.TODOS,
    )
    productos = models.ManyToManyField(
        "productos.Producto",
        blank=True,
        related_name="promociones",
    )
    categorias = models.ManyToManyField(
        "productos.Categoria",
        blank=True,
        related_name="promociones",
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "promociones"
        ordering = ["-fecha_inicio", "nombre"]
        verbose_name = "promocion"
        verbose_name_plural = "promociones"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["tipo_promocion"]),
            models.Index(fields=["canal_venta"]),
            models.Index(fields=["activa"]),
            models.Index(fields=["fecha_inicio", "fecha_fin"]),
        ]

    def __str__(self) -> str:
        return self.nombre

    def esta_vigente(self) -> bool:
        """Indica si la promocion esta activa dentro del rango de fechas."""

        ahora = timezone.now()

        return self.activa and self.fecha_inicio <= ahora <= self.fecha_fin
