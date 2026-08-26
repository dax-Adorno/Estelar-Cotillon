"""Reportes comerciales internos."""

from decimal import Decimal
from typing import Any

from django.db.models import Count, Sum
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pedidos.models import DetallePedido, Pedido
from apps.clientes.permissions import EsOperadorOAdmin
from apps.productos.models import Categoria, Producto
from apps.promociones.models import Promocion

STOCK_BAJO_UMBRAL = 10


def _decimal_a_texto(valor: Any) -> str:
    """Convierte valores decimales agregados a texto seguro para JSON."""
    if isinstance(valor, Decimal):
        return f"{valor:.2f}"

    return "0.00"


def _entero(valor: Any) -> int:
    """Convierte agregados numericos nulos a entero."""
    if isinstance(valor, int):
        return valor

    return 0


def _metricas_generales() -> dict[str, Any]:
    """Construye metricas generales del negocio."""
    total_estimado = Pedido.objects.aggregate(
        total=Sum("total"),
    )["total"]

    unidades_pedidas = DetallePedido.objects.aggregate(
        total=Sum("cantidad"),
    )["total"]

    return {
        "pedidos_total": Pedido.objects.count(),
        "pedidos_pendientes": Pedido.objects.filter(
            estado=Pedido.EstadoPedido.PENDIENTE,
        ).count(),
        "total_estimado": _decimal_a_texto(total_estimado),
        "unidades_pedidas": _entero(unidades_pedidas),
        "productos_activos": Producto.objects.filter(activo=True).count(),
        "productos_stock_bajo": Producto.objects.filter(
            activo=True,
            stock__lte=STOCK_BAJO_UMBRAL,
        ).count(),
        "categorias_activas": Categoria.objects.filter(activa=True).count(),
        "promociones_activas": Promocion.objects.filter(activa=True).count(),
    }


def _pedidos_por_estado() -> list[dict[str, Any]]:
    """Agrupa pedidos por estado."""
    resultados = (
        Pedido.objects.values("estado")
        .annotate(cantidad=Count("id"))
        .order_by("estado")
    )

    return [
        {
            "estado": resultado["estado"],
            "cantidad": _entero(resultado["cantidad"]),
        }
        for resultado in resultados
    ]


def _pedidos_por_canal() -> list[dict[str, Any]]:
    """Agrupa pedidos por canal de venta."""
    resultados = (
        Pedido.objects.values("canal_venta")
        .annotate(cantidad=Count("id"))
        .order_by("canal_venta")
    )

    return [
        {
            "canal_venta": resultado["canal_venta"],
            "cantidad": _entero(resultado["cantidad"]),
        }
        for resultado in resultados
    ]


def _top_productos() -> list[dict[str, Any]]:
    """Devuelve productos mas pedidos."""
    productos = (
        DetallePedido.objects.values(
            "producto_id",
            "producto__sku",
            "producto__nombre",
        )
        .annotate(
            unidades=Sum("cantidad"),
            importe=Sum("subtotal"),
        )
        .order_by("-unidades", "producto__nombre")[:5]
    )

    return [
        {
            "producto_id": producto["producto_id"],
            "sku": producto["producto__sku"],
            "nombre": producto["producto__nombre"],
            "unidades": _entero(producto["unidades"]),
            "importe": _decimal_a_texto(producto["importe"]),
        }
        for producto in productos
    ]


def _productos_stock_bajo() -> list[dict[str, Any]]:
    """Devuelve productos activos con stock bajo."""
    productos = Producto.objects.filter(
        activo=True,
        stock__lte=STOCK_BAJO_UMBRAL,
    ).order_by("stock", "nombre")[:10]

    return [
        {
            "id": producto.id,
            "sku": producto.sku,
            "nombre": producto.nombre,
            "stock": producto.stock,
        }
        for producto in productos
    ]


class ResumenComercialAPIView(APIView):
    """Endpoint interno de resumen comercial."""

    permission_classes = (EsOperadorOAdmin,)

    def get(self, request: Request) -> Response:
        """Devuelve metricas basicas del negocio."""
        return Response(
            {
                "metricas": _metricas_generales(),
                "pedidos_por_estado": _pedidos_por_estado(),
                "pedidos_por_canal": _pedidos_por_canal(),
                "top_productos": _top_productos(),
                "productos_stock_bajo": _productos_stock_bajo(),
            },
        )
