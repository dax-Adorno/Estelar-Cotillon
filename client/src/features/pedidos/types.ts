import type { CarritoItem } from "../carrito/types";

export interface DatosPedidoCliente {
  nombreCompleto: string;
  email: string;
  whatsapp: string;
  notas: string;
}

export interface PedidoPublicoItemPayload {
  producto_id: number;
  cantidad: number;
}

export interface PedidoPublicoCreatePayload {
  nombre_completo: string;
  email: string;
  whatsapp: string;
  notas: string;
  items: PedidoPublicoItemPayload[];
}

export interface PedidoPublicoResponse {
  id: number;
  codigo: string;
  cliente_nombre: string;
  estado: string;
  estado_pago: string;
  canal_venta: string;
  subtotal: string;
  descuento: string;
  total: string;
  promocion_nombre: string;
  creado_en: string;
}

export function mapearItemsCarritoParaPedido(
  items: CarritoItem[],
): PedidoPublicoItemPayload[] {
  return items.map((item) => ({
    producto_id: item.producto.id,
    cantidad: item.cantidad,
  }));
}
