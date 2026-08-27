"""Motor determinista para calcular promociones aplicables."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Q
from django.utils import timezone

from apps.productos.models import Producto
from apps.promociones.models import Promocion

CENTAVO = Decimal("0.01")


@dataclass(frozen=True)
class LineaPromocion:
    """Item comercial usado por el motor sin depender del request."""

    producto: Producto
    cantidad: int
    precio_unitario: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.precio_unitario * self.cantidad


@dataclass(frozen=True)
class ResultadoPromocion:
    """Mejor beneficio encontrado para el pedido."""

    promocion: Promocion
    descuento: Decimal


def calcular_mejor_promocion(
    *,
    lineas: list[LineaPromocion],
    subtotal: Decimal,
    canal_venta: str,
    mayorista_aprobado: bool,
) -> ResultadoPromocion | None:
    """Elige un solo beneficio para impedir descuentos acumulados accidentales."""
    ahora = timezone.now()
    promociones = (
        Promocion.objects.filter(
            activa=True,
            fecha_inicio__lte=ahora,
            fecha_fin__gte=ahora,
        )
        .filter(Q(canal_venta=Promocion.CanalVenta.TODOS) | Q(canal_venta=canal_venta))
        .prefetch_related(
            "productos",
            "categorias",
            "items_combo__producto",
        )
        .order_by("pk")
    )

    mejor: ResultadoPromocion | None = None
    for promocion in promociones:
        descuento = _calcular_descuento(
            promocion=promocion,
            lineas=lineas,
            subtotal=subtotal,
            mayorista_aprobado=mayorista_aprobado,
        )
        if descuento <= Decimal("0"):
            continue
        descuento = min(descuento, subtotal).quantize(CENTAVO, rounding=ROUND_HALF_UP)
        if mejor is None or descuento > mejor.descuento:
            mejor = ResultadoPromocion(promocion=promocion, descuento=descuento)
    return mejor


def _calcular_descuento(
    *,
    promocion: Promocion,
    lineas: list[LineaPromocion],
    subtotal: Decimal,
    mayorista_aprobado: bool,
) -> Decimal:
    if promocion.compra_minima is not None and subtotal < promocion.compra_minima:
        return Decimal("0")
    if (
        promocion.tipo_promocion == Promocion.TipoPromocion.MAYORISTA
        and not mayorista_aprobado
    ):
        return Decimal("0")
    if promocion.tipo_promocion == Promocion.TipoPromocion.ENVIO_GRATIS:
        return Decimal("0")
    if promocion.tipo_promocion == Promocion.TipoPromocion.COMBO:
        return _calcular_combo(promocion, lineas)

    subtotal_aplicable = _subtotal_aplicable(promocion, lineas)
    return _aplicar_valor_descuento(promocion, subtotal_aplicable)


def _subtotal_aplicable(
    promocion: Promocion,
    lineas: list[LineaPromocion],
) -> Decimal:
    productos = {producto.pk for producto in promocion.productos.all()}
    categorias = {categoria.pk for categoria in promocion.categorias.all()}
    if not productos and not categorias:
        return sum((linea.subtotal for linea in lineas), Decimal("0"))
    return sum(
        (
            linea.subtotal
            for linea in lineas
            if linea.producto.pk in productos
            or linea.producto.categoria_id in categorias
        ),
        Decimal("0"),
    )


def _calcular_combo(
    promocion: Promocion,
    lineas: list[LineaPromocion],
) -> Decimal:
    requeridos = list(promocion.items_combo.all())
    if not requeridos:
        return Decimal("0")
    lineas_por_producto = {linea.producto.pk: linea for linea in lineas}
    repeticiones: list[int] = []
    for item in requeridos:
        linea = lineas_por_producto.get(item.producto_id)
        if linea is None or item.cantidad < 1:
            return Decimal("0")
        repeticiones.append(linea.cantidad // item.cantidad)
    cantidad_combos = min(repeticiones, default=0)
    if cantidad_combos < 1:
        return Decimal("0")

    subtotal_combo = sum(
        (
            lineas_por_producto[item.producto_id].precio_unitario
            * item.cantidad
            * cantidad_combos
            for item in requeridos
        ),
        Decimal("0"),
    )
    if promocion.monto_descuento is not None:
        return promocion.monto_descuento * cantidad_combos
    return _aplicar_valor_descuento(promocion, subtotal_combo)


def _aplicar_valor_descuento(
    promocion: Promocion,
    subtotal_aplicable: Decimal,
) -> Decimal:
    if subtotal_aplicable <= Decimal("0"):
        return Decimal("0")
    if promocion.porcentaje_descuento is not None:
        return subtotal_aplicable * promocion.porcentaje_descuento / Decimal("100")
    if promocion.monto_descuento is not None:
        return min(promocion.monto_descuento, subtotal_aplicable)
    return Decimal("0")
