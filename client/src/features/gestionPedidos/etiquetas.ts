import type { EstadoPago, EstadoPedido } from "./types";

export const ETIQUETAS_ESTADO: Record<EstadoPedido, string> = {
  borrador: "Borrador",
  pendiente: "Pendiente",
  confirmado: "Confirmado",
  entregado: "Entregado",
  cancelado: "Cancelado",
};

export const ETIQUETAS_PAGO: Record<EstadoPago, string> = {
  pendiente: "Pendiente",
  parcial: "Pago parcial",
  pagado: "Pagado",
  reembolsado: "Reembolsado",
};
