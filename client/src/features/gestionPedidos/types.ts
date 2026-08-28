export type EstadoPedido =
  | "borrador"
  | "pendiente"
  | "confirmado"
  | "entregado"
  | "cancelado";

export type EstadoPago = "pendiente" | "parcial" | "pagado" | "reembolsado";

export type CanalVenta =
  | "web"
  | "whatsapp"
  | "instagram"
  | "mercado_libre"
  | "tienda_nube"
  | "presencial";

export interface PaginaPedidos<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface PedidoResumen {
  id: number;
  cliente: number;
  cliente_nombre: string;
  cliente_email: string;
  codigo: string;
  estado: EstadoPedido;
  estado_pago: EstadoPago;
  canal_venta: CanalVenta;
  total: string;
  promocion_nombre: string;
  cantidad_items: number;
  cantidad_unidades: number;
  creado_en: string;
  actualizado_en: string;
}

export interface LineaPedido {
  id: number;
  pedido: number;
  producto: number;
  producto_nombre: string;
  producto_sku: string;
  cantidad: number;
  precio_unitario: string;
  subtotal: string;
  creado_en: string;
  actualizado_en: string;
}

export interface EventoPedido {
  id: number;
  tipo: "estado" | "estado_pago";
  valor_anterior: string;
  valor_nuevo: string;
  comentario: string;
  usuario_email: string;
  creado_en: string;
}

export interface PedidoDetalle {
  id: number;
  cliente: number;
  cliente_nombre: string;
  codigo: string;
  estado: EstadoPedido;
  estado_pago: EstadoPago;
  canal_venta: CanalVenta;
  subtotal: string;
  descuento: string;
  total: string;
  promocion_aplicada: number | null;
  promocion_nombre: string;
  notas: string;
  detalles: LineaPedido[];
  eventos: EventoPedido[];
  creado_en: string;
  actualizado_en: string;
}

export interface FiltrosPedidos {
  search?: string;
  estado?: EstadoPedido;
  estado_pago?: EstadoPago;
  canal_venta?: CanalVenta;
  desde?: string;
  hasta?: string;
  ordering?: "-creado_en" | "creado_en" | "-total" | "total";
  page?: number;
}
