import { apiRequest, getApi } from "../../lib/api";
import type { FiltrosClientes, PaginaClientes, PerfilPayload } from "./types";

function queryString(filtros: FiltrosClientes): string {
  const query = new URLSearchParams({ page_size: "25" });
  Object.entries(filtros).forEach(([clave, valor]) => {
    if (valor !== undefined && String(valor).length > 0) query.set(clave, String(valor));
  });
  return query.toString();
}

export function listarClientes(filtros: FiltrosClientes = {}): Promise<PaginaClientes> {
  return getApi<PaginaClientes>(`/clientes/?${queryString(filtros)}`);
}

export function actualizarPerfil(perfilId: number, payload: PerfilPayload): Promise<unknown> {
  return apiRequest(`/perfiles-usuario/${perfilId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
