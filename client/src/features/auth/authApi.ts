import { ApiError, apiRequest } from "../../lib/api";
import type {
  MensajeApi,
  RegistroMayoristaPayload,
  UsuarioActual,
} from "./types";

const ROLES_VALIDOS = new Set([
  "cliente_minorista",
  "cliente_mayorista",
  "operador",
  "admin",
]);

function esUsuarioActual(data: unknown): data is UsuarioActual {
  if (!data || typeof data !== "object") {
    return false;
  }

  const usuario = data as Partial<UsuarioActual>;
  return (
    typeof usuario.id === "number" &&
    typeof usuario.email === "string" &&
    typeof usuario.nombre === "string" &&
    typeof usuario.apellido === "string" &&
    typeof usuario.rol === "string" &&
    ROLES_VALIDOS.has(usuario.rol) &&
    typeof usuario.mayorista_aprobado === "boolean"
  );
}

export async function obtenerSesionActual(): Promise<UsuarioActual | null> {
  try {
    const data = await apiRequest<unknown>("/auth/me/");
    return esUsuarioActual(data) ? data : null;
  } catch (error) {
    if (error instanceof ApiError && [401, 403].includes(error.status)) {
      return null;
    }
    throw error;
  }
}

export async function iniciarSesion(
  email: string,
  password: string,
): Promise<UsuarioActual> {
  return apiRequest<UsuarioActual>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function cerrarSesion(): Promise<void> {
  await apiRequest<void>("/auth/logout/", { method: "POST" });
}

export async function registrarMayorista(
  payload: RegistroMayoristaPayload,
): Promise<MensajeApi> {
  return apiRequest<MensajeApi>("/auth/registro/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function solicitarRestablecimiento(
  email: string,
): Promise<MensajeApi> {
  return apiRequest<MensajeApi>("/auth/password-reset/", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function verificarEmail(
  uid: string,
  token: string,
): Promise<MensajeApi> {
  return apiRequest<MensajeApi>("/auth/verificar-email/", {
    method: "POST",
    body: JSON.stringify({ uid, token }),
  });
}

export async function confirmarRestablecimiento(
  uid: string,
  token: string,
  password: string,
  passwordConfirmacion: string,
): Promise<MensajeApi> {
  return apiRequest<MensajeApi>("/auth/password-reset-confirm/", {
    method: "POST",
    body: JSON.stringify({
      uid,
      token,
      password,
      password_confirmacion: passwordConfirmacion,
    }),
  });
}
