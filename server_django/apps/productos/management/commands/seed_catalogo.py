"""Comando para cargar datos iniciales de catalogo."""

# pylint: disable=too-many-locals

from datetime import timedelta
from decimal import Decimal
from typing import Any, TypedDict

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.productos.models import Categoria, Producto
from apps.promociones.models import ItemComboPromocion, Promocion


class CategoriaSeed(TypedDict):
    """Estructura tipada para categorias de prueba."""

    slug: str
    nombre: str
    descripcion: str


class ProductoSeed(TypedDict):
    """Estructura tipada para productos de prueba."""

    categoria_slug: str
    sku: str
    nombre: str
    slug: str
    descripcion: str
    precio_minorista: Decimal
    precio_mayorista: Decimal
    cantidad_minima_mayorista: int
    stock: int
    destacado: bool


class Command(BaseCommand):
    """Carga datos de catalogo para desarrollo y demo."""

    help = "Carga categorias, productos y promociones de ejemplo."

    def handle(self, *_args: Any, **_options: Any) -> None:
        categorias = self._crear_categorias()
        productos = self._crear_productos(categorias)
        self._crear_promociones(categorias, productos)

        self.stdout.write(
            self.style.SUCCESS("Catalogo de prueba cargado correctamente.")
        )

    def _crear_categorias(self) -> dict[str, Categoria]:
        categorias_data: list[CategoriaSeed] = [
            {
                "slug": "limpiapipas",
                "nombre": "Limpiapipas",
                "descripcion": "Insumos flexibles para manualidades, decoración y kits creativos.",
            },
            {
                "slug": "slime-y-gel",
                "nombre": "Slime y gel",
                "descripcion": "Kits, bases y accesorios para experiencias sensoriales.",
            },
            {
                "slug": "glitter-y-brillos",
                "nombre": "Glitter y brillos",
                "descripcion": "Brillos decorativos para manualidades, eventos y packaging.",
            },
            {
                "slug": "bijou-creativa",
                "nombre": "Bijou creativa",
                "descripcion": "Mostacillas, dijes y componentes para accesorios personalizados.",
            },
            {
                "slug": "decoracion-fiestas",
                "nombre": "Decoración para fiestas",
                "descripcion": "Insumos decorativos para eventos, cumpleaños y ambientaciones.",
            },
        ]

        categorias: dict[str, Categoria] = {}

        for categoria_data in categorias_data:
            categoria, _created = Categoria.objects.update_or_create(
                slug=categoria_data["slug"],
                defaults={
                    "nombre": categoria_data["nombre"],
                    "descripcion": categoria_data["descripcion"],
                    "activa": True,
                },
            )
            categorias[categoria.slug] = categoria

        return categorias

    def _crear_productos(
        self,
        categorias: dict[str, Categoria],
    ) -> dict[str, Producto]:
        productos_data: list[ProductoSeed] = [
            {
                "categoria_slug": "limpiapipas",
                "sku": "LIM-001",
                "nombre": "Limpiapipas surtidos 30 cm",
                "slug": "limpiapipas-surtidos-30-cm",
                "descripcion": "Pack de limpiapipas de colores surtidos para manualidades.",
                "precio_minorista": Decimal("1500.00"),
                "precio_mayorista": Decimal("1200.00"),
                "cantidad_minima_mayorista": 10,
                "stock": 180,
                "destacado": True,
            },
            {
                "categoria_slug": "limpiapipas",
                "sku": "LIM-002",
                "nombre": "Limpiapipas metalizados",
                "slug": "limpiapipas-metalizados",
                "descripcion": "Limpiapipas con terminación metalizada para decoración.",
                "precio_minorista": Decimal("2200.00"),
                "precio_mayorista": Decimal("1750.00"),
                "cantidad_minima_mayorista": 10,
                "stock": 90,
                "destacado": True,
            },
            {
                "categoria_slug": "slime-y-gel",
                "sku": "SLI-001",
                "nombre": "Kit slime colores pastel",
                "slug": "kit-slime-colores-pastel",
                "descripcion": "Kit creativo para armado de slime con accesorios incluidos.",
                "precio_minorista": Decimal("8500.00"),
                "precio_mayorista": Decimal("7200.00"),
                "cantidad_minima_mayorista": 5,
                "stock": 35,
                "destacado": True,
            },
            {
                "categoria_slug": "glitter-y-brillos",
                "sku": "GLI-001",
                "nombre": "Glitter extra fino dorado",
                "slug": "glitter-extra-fino-dorado",
                "descripcion": "Glitter dorado para manualidades, uñas, eventos y packaging.",
                "precio_minorista": Decimal("1900.00"),
                "precio_mayorista": Decimal("1500.00"),
                "cantidad_minima_mayorista": 12,
                "stock": 120,
                "destacado": False,
            },
            {
                "categoria_slug": "bijou-creativa",
                "sku": "BIJ-001",
                "nombre": "Set mostacillas multicolor",
                "slug": "set-mostacillas-multicolor",
                "descripcion": "Mostacillas surtidas para pulseras, bijou y accesorios.",
                "precio_minorista": Decimal("3200.00"),
                "precio_mayorista": Decimal("2600.00"),
                "cantidad_minima_mayorista": 8,
                "stock": 70,
                "destacado": False,
            },
            {
                "categoria_slug": "decoracion-fiestas",
                "sku": "DEC-001",
                "nombre": "Guirnalda papel seda",
                "slug": "guirnalda-papel-seda",
                "descripcion": "Guirnalda decorativa para fiestas y ambientaciones.",
                "precio_minorista": Decimal("2800.00"),
                "precio_mayorista": Decimal("2300.00"),
                "cantidad_minima_mayorista": 6,
                "stock": 55,
                "destacado": False,
            },
        ]

        productos: dict[str, Producto] = {}

        for producto_data in productos_data:
            categoria_slug = producto_data["categoria_slug"]

            producto, _created = Producto.objects.update_or_create(
                sku=producto_data["sku"],
                defaults={
                    "categoria": categorias[str(categoria_slug)],
                    "nombre": producto_data["nombre"],
                    "slug": producto_data["slug"],
                    "descripcion": producto_data["descripcion"],
                    "precio_minorista": producto_data["precio_minorista"],
                    "precio_mayorista": producto_data["precio_mayorista"],
                    "cantidad_minima_mayorista": producto_data[
                        "cantidad_minima_mayorista"
                    ],
                    "stock": producto_data["stock"],
                    "activo": True,
                    "destacado": producto_data["destacado"],
                },
            )
            productos[producto.sku] = producto

        return productos

    def _crear_promociones(
        self,
        categorias: dict[str, Categoria],
        productos: dict[str, Producto],
    ) -> None:
        ahora = timezone.now()

        mayorista, _created = Promocion.objects.update_or_create(
            slug="mayorista-creativo",
            defaults={
                "nombre": "Mayorista creativo",
                "descripcion": "Beneficio para compras mayoristas de insumos creativos.",
                "tipo_promocion": Promocion.TipoPromocion.MAYORISTA,
                "porcentaje_descuento": Decimal("10.00"),
                "monto_descuento": None,
                "compra_minima": Decimal("30000.00"),
                "canal_venta": Promocion.CanalVenta.TODOS,
                "fecha_inicio": ahora - timedelta(days=1),
                "fecha_fin": ahora + timedelta(days=45),
                "activa": True,
            },
        )
        mayorista.productos.set(
            [
                productos["LIM-001"],
                productos["LIM-002"],
                productos["GLI-001"],
            ]
        )
        mayorista.categorias.set(
            [
                categorias["limpiapipas"],
                categorias["glitter-y-brillos"],
            ]
        )

        combo_slime, _created = Promocion.objects.update_or_create(
            slug="combo-slime-escolar",
            defaults={
                "nombre": "Combo slime escolar",
                "descripcion": "Descuento especial para kits slime por volumen.",
                "tipo_promocion": Promocion.TipoPromocion.COMBO,
                "porcentaje_descuento": None,
                "monto_descuento": Decimal("2000.00"),
                "compra_minima": Decimal("15000.00"),
                "canal_venta": Promocion.CanalVenta.WEB,
                "fecha_inicio": ahora - timedelta(days=1),
                "fecha_fin": ahora + timedelta(days=30),
                "activa": True,
            },
        )
        combo_slime.productos.set([productos["SLI-001"]])
        combo_slime.categorias.set([categorias["slime-y-gel"]])
        ItemComboPromocion.objects.update_or_create(
            promocion=combo_slime,
            producto=productos["SLI-001"],
            defaults={"cantidad": 2},
        )
        combo_slime.items_combo.exclude(producto=productos["SLI-001"]).delete()

        promo_instagram, _created = Promocion.objects.update_or_create(
            slug="promo-instagram-glitter",
            defaults={
                "nombre": "Promo Instagram glitter",
                "descripcion": "Promoción orientada a campañas de Instagram.",
                "tipo_promocion": Promocion.TipoPromocion.PORCENTAJE,
                "porcentaje_descuento": Decimal("15.00"),
                "monto_descuento": None,
                "compra_minima": Decimal("10000.00"),
                "canal_venta": Promocion.CanalVenta.INSTAGRAM,
                "fecha_inicio": ahora - timedelta(days=1),
                "fecha_fin": ahora + timedelta(days=20),
                "activa": True,
            },
        )
        promo_instagram.productos.set([productos["GLI-001"]])
        promo_instagram.categorias.set([categorias["glitter-y-brillos"]])
