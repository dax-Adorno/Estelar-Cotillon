"""Reglas transaccionales para la operacion de pedidos."""

from collections.abc import Iterable
from typing import Any

from django.db import transaction
from django.db.models import Sum

from apps.pedidos.models import EventoPedido, Pedido
from apps.productos.models import Producto


class TransicionPedidoError(ValueError):
    """Indica que una operacion no respeta el flujo comercial."""


TRANSICIONES_ESTADO: dict[str, set[str]] = {
    Pedido.EstadoPedido.BORRADOR: {
        Pedido.EstadoPedido.PENDIENTE,
        Pedido.EstadoPedido.CANCELADO,
    },
    Pedido.EstadoPedido.PENDIENTE: {
        Pedido.EstadoPedido.CONFIRMADO,
        Pedido.EstadoPedido.CANCELADO,
    },
    Pedido.EstadoPedido.CONFIRMADO: {
        Pedido.EstadoPedido.ENTREGADO,
        Pedido.EstadoPedido.CANCELADO,
    },
    Pedido.EstadoPedido.ENTREGADO: set(),
    Pedido.EstadoPedido.CANCELADO: set(),
}

TRANSICIONES_PAGO: dict[str, set[str]] = {
    Pedido.EstadoPago.PENDIENTE: {
        Pedido.EstadoPago.PARCIAL,
        Pedido.EstadoPago.PAGADO,
    },
    Pedido.EstadoPago.PARCIAL: {
        Pedido.EstadoPago.PAGADO,
        Pedido.EstadoPago.REEMBOLSADO,
    },
    Pedido.EstadoPago.PAGADO: {Pedido.EstadoPago.REEMBOLSADO},
    Pedido.EstadoPago.REEMBOLSADO: set(),
}


@transaction.atomic
def cambiar_estado_pedido(
    *,
    pedido_id: int,
    nuevo_estado: str,
    usuario: Any,
    comentario: str = "",
) -> Pedido:
    """Cambia estado, reserva o repone stock y registra auditoria."""
    pedido = (
        Pedido.objects.select_for_update().select_related("cliente").get(pk=pedido_id)
    )
    estado_anterior = pedido.estado
    permitidos = TRANSICIONES_ESTADO.get(estado_anterior, set())
    if nuevo_estado not in permitidos:
        raise TransicionPedidoError(
            f"No se puede cambiar el pedido de {estado_anterior} a {nuevo_estado}.",
        )

    if nuevo_estado == Pedido.EstadoPedido.CANCELADO and pedido.estado_pago in {
        Pedido.EstadoPago.PARCIAL,
        Pedido.EstadoPago.PAGADO,
    }:
        raise TransicionPedidoError(
            "Debe registrar el reembolso antes de cancelar un pedido cobrado.",
        )

    if (
        estado_anterior == Pedido.EstadoPedido.PENDIENTE
        and nuevo_estado == Pedido.EstadoPedido.CONFIRMADO
    ):
        _descontar_stock(pedido)
    elif (
        estado_anterior == Pedido.EstadoPedido.CONFIRMADO
        and nuevo_estado == Pedido.EstadoPedido.CANCELADO
    ):
        _reponer_stock(pedido)

    pedido.estado = nuevo_estado
    pedido.save(update_fields=["estado", "actualizado_en"])
    EventoPedido.objects.create(
        pedido=pedido,
        tipo=EventoPedido.TipoEvento.ESTADO,
        valor_anterior=estado_anterior,
        valor_nuevo=nuevo_estado,
        comentario=comentario.strip(),
        usuario=usuario if getattr(usuario, "is_authenticated", False) else None,
    )
    return pedido


@transaction.atomic
def cambiar_estado_pago_pedido(
    *,
    pedido_id: int,
    nuevo_estado: str,
    usuario: Any,
    comentario: str = "",
) -> Pedido:
    """Actualiza el pago respetando su secuencia y deja trazabilidad."""
    pedido = (
        Pedido.objects.select_for_update().select_related("cliente").get(pk=pedido_id)
    )
    estado_anterior = pedido.estado_pago
    permitidos = TRANSICIONES_PAGO.get(estado_anterior, set())
    if nuevo_estado not in permitidos:
        raise TransicionPedidoError(
            "No se puede cambiar el pago " f"de {estado_anterior} a {nuevo_estado}.",
        )

    pedido.estado_pago = nuevo_estado
    pedido.save(update_fields=["estado_pago", "actualizado_en"])
    EventoPedido.objects.create(
        pedido=pedido,
        tipo=EventoPedido.TipoEvento.ESTADO_PAGO,
        valor_anterior=estado_anterior,
        valor_nuevo=nuevo_estado,
        comentario=comentario.strip(),
        usuario=usuario if getattr(usuario, "is_authenticated", False) else None,
    )
    return pedido


def _cantidades_por_producto(pedido: Pedido) -> dict[int, int]:
    """Agrupa cantidades incluso si existen lineas repetidas heredadas."""
    cantidades = pedido.detalles.values("producto_id").annotate(total=Sum("cantidad"))
    return {
        int(elemento["producto_id"]): int(elemento["total"] or 0)
        for elemento in cantidades
    }


def _bloquear_productos(producto_ids: Iterable[int]) -> dict[int, Producto]:
    """Bloquea productos en orden estable para evitar carreras y deadlocks."""
    productos = (
        Producto.objects.select_for_update().filter(pk__in=producto_ids).order_by("pk")
    )
    return {producto.pk: producto for producto in productos}


def _descontar_stock(pedido: Pedido) -> None:
    """Reserva stock al confirmar el pedido."""
    cantidades = _cantidades_por_producto(pedido)
    if not cantidades:
        raise TransicionPedidoError("No se puede confirmar un pedido sin productos.")
    productos = _bloquear_productos(cantidades)
    if len(productos) != len(cantidades):
        raise TransicionPedidoError("Uno de los productos del pedido ya no existe.")

    for producto_id, cantidad in cantidades.items():
        producto = productos[producto_id]
        if producto.stock < cantidad:
            raise TransicionPedidoError(
                f"Stock insuficiente para {producto.sku}: "
                f"disponible {producto.stock}, solicitado {cantidad}.",
            )

    for producto_id, cantidad in cantidades.items():
        producto = productos[producto_id]
        producto.stock -= cantidad
        producto.save(update_fields=["stock", "actualizado_en"])


def _reponer_stock(pedido: Pedido) -> None:
    """Libera stock cuando se cancela un pedido previamente confirmado."""
    cantidades = _cantidades_por_producto(pedido)
    productos = _bloquear_productos(cantidades)
    for producto_id, cantidad in cantidades.items():
        producto = productos.get(producto_id)
        if producto is None:
            continue
        producto.stock += cantidad
        producto.save(update_fields=["stock", "actualizado_en"])
