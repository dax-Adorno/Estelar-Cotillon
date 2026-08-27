import { getApi } from "../../lib/api";
import type { ResumenComercial } from "./types";

export async function obtenerResumenComercial(): Promise<ResumenComercial> {
  return getApi<ResumenComercial>("/reportes/resumen-comercial/");
}
