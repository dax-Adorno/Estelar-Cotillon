export type RolUsuario =
  | "cliente_minorista"
  | "cliente_mayorista"
  | "operador"
  | "admin";

export interface UsuarioActual {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  rol: RolUsuario;
  mayorista_aprobado: boolean;
}

export interface RegistroMayoristaPayload {
  nombre: string;
  apellido: string;
  email: string;
  whatsapp: string;
  tipo_cliente: "mayorista";
  razon_social: string;
  cuit: string;
  password: string;
  password_confirmacion: string;
}

export interface MensajeApi {
  detalle: string;
}
