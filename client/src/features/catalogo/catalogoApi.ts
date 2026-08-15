import { getApi } from "../../lib/api";
import type { Categoria, Producto, Promocion } from "./types";

export function obtenerCategorias(): Promise<Categoria[]> {
  return getApi<Categoria[]>("/categorias/");
}

export function obtenerProductos(): Promise<Producto[]> {
  return getApi<Producto[]>("/productos/");
}

export function obtenerPromociones(): Promise<Promocion[]> {
  return getApi<Promocion[]>("/promociones/");
}
