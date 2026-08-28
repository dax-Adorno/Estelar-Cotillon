import { apiRequest, getApi } from "../../lib/api";
import type {
  EstadoPago,
  EstadoPedido,
  FiltrosPedidos,
  PaginaPedidos,
  PedidoDetalle,
  PedidoResumen,
} from "./types";

function construirQuery(filtros: FiltrosPedidos): string {
  const query = new URLSearchParams({ page_size: "25" });
  Object.entries(filtros).forEach(([clave, valor]) => {
    if (valor !== undefined && String(valor).length > 0) query.set(clave, String(valor));
  });
  return query.toString();
}

export function listarPedidos(filtros: FiltrosPedidos = {}): Promise<PaginaPedidos<PedidoResumen>> {
  return getApi<PaginaPedidos<PedidoResumen>>(`/pedidos/?${construirQuery(filtros)}`);
}

export function obtenerPedido(pedidoId: number): Promise<PedidoDetalle> {
  return getApi<PedidoDetalle>(`/pedidos/${pedidoId}/`);
}

export function cambiarEstadoPedido(
  pedidoId: number,
  estado: EstadoPedido,
  comentario: string,
): Promise<PedidoDetalle> {
  return apiRequest<PedidoDetalle>(`/pedidos/${pedidoId}/cambiar-estado/`, {
    method: "POST",
    body: JSON.stringify({ estado, comentario }),
  });
}

export function cambiarEstadoPago(
  pedidoId: number,
  estadoPago: EstadoPago,
  comentario: string,
): Promise<PedidoDetalle> {
  return apiRequest<PedidoDetalle>(`/pedidos/${pedidoId}/cambiar-estado-pago/`, {
    method: "POST",
    body: JSON.stringify({ estado_pago: estadoPago, comentario }),
  });
}
