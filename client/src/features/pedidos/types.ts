import type { CarritoItem } from "../carrito/types";

export interface DatosPedidoCliente {
  nombreCompleto: string;
  email: string;
  whatsapp: string;
  notas: string;
}

export interface PedidoPreparado {
  cliente: DatosPedidoCliente;
  items: CarritoItem[];
  total: number;
  creadoEn: string;
}
