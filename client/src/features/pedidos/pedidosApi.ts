import type { CarritoItem } from "../carrito/types";
import type {
  DatosPedidoCliente,
  PedidoPublicoCreatePayload,
  PedidoPublicoResponse,
} from "./types";
import { mapearItemsCarritoParaPedido } from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

function construirUrlApi(path: string): string {
  const baseUrl = API_BASE_URL.replace(/\/$/, "");
  const cleanPath = path.replace(/^\//, "");

  return `${baseUrl}/${cleanPath}`;
}

async function obtenerMensajeError(response: Response): Promise<string> {
  const data: unknown = await response.json().catch(() => null);

  if (data && typeof data === "object" && "detail" in data) {
    const detalle = data.detail;

    if (typeof detalle === "string") {
      return detalle;
    }
  }

  return "No se pudo crear el pedido. Revisá los datos e intentá nuevamente.";
}

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
  const response = await fetch(construirUrlApi("/pedidos-publicos/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await obtenerMensajeError(response));
  }

  return response.json() as Promise<PedidoPublicoResponse>;
}
