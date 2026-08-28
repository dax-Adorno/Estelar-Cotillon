import type { RolUsuario } from "../auth/types";

export type TipoCliente = "minorista" | "mayorista";
export type EstadoCuenta =
  | "sin_cuenta"
  | "minorista"
  | "mayorista_pendiente"
  | "mayorista_aprobado"
  | "operador"
  | "admin";

export interface ClienteGestion {
  id: number;
  nombre: string;
  apellido: string;
  razon_social: string;
  tipo_cliente: TipoCliente;
  email: string;
  telefono: string;
  whatsapp: string;
  documento: string;
  cuit: string;
  direccion: string;
  ciudad: string;
  provincia: string;
  notas: string;
  activo: boolean;
  pedidos_total: number;
  total_comprado: string;
  ultimo_pedido_en: string | null;
  perfil_id: number | null;
  rol: RolUsuario | null;
  mayorista_aprobado: boolean;
  creado_en: string;
  actualizado_en: string;
}

export interface PaginaClientes {
  count: number;
  next: string | null;
  previous: string | null;
  results: ClienteGestion[];
}

export interface FiltrosClientes {
  search?: string;
  tipo_cliente?: TipoCliente;
  cuenta?: EstadoCuenta;
  ordering?: "nombre" | "-creado_en" | "-ultimo_pedido_en" | "-pedidos_total" | "-total_comprado";
  page?: number;
}

export interface PerfilPayload {
  rol?: Exclude<RolUsuario, "admin">;
  mayorista_aprobado?: boolean;
}
