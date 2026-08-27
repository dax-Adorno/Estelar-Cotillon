import type { CarritoItem } from "../carrito/types";
import { apiRequest } from "../../lib/api";
import type {
  DatosPedidoCliente,
  PedidoPublicoCreatePayload,
  PedidoPublicoResponse,
} from "./types";
import { mapearItemsCarritoParaPedido } from "./types";

export function construirPedidoPublicoPayload(
  datosCliente: DatosPedidoCliente,
  items: CarritoItem[],
): PedidoPublicoCreatePayload {
  return {
    nombre_completo: datosCliente.nombreCompleto,
    email: datosCliente.email,
    whatsapp: datosCliente.whatsapp,
    notas: datosCliente.notas,
    items: mapearItemsCarritoParaPedido(items),
  };
}

export async function crearPedidoPublico(
  payload: PedidoPublicoCreatePayload,
): Promise<PedidoPublicoResponse> {
  return apiRequest<PedidoPublicoResponse>("/pedidos-publicos/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
