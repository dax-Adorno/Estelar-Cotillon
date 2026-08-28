import { apiRequest, getApi } from "../../lib/api";
import type {
  CategoriaGestion,
  CategoriaPayload,
  ImagenProductoGestion,
  PaginaApi,
  ProductoGestion,
  ProductoPayload,
} from "./types";

function queryString(params: Record<string, string | number | undefined>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && String(value).length > 0) {
      query.set(key, String(value));
    }
  });
  return query.toString();
}

export function listarCategoriasGestion(): Promise<PaginaApi<CategoriaGestion>> {
  return getApi<PaginaApi<CategoriaGestion>>(
    "/gestion/categorias/?page_size=100",
  );
}

export function guardarCategoria(
  payload: CategoriaPayload,
  categoriaId?: number,
): Promise<CategoriaGestion> {
  return apiRequest<CategoriaGestion>(
    categoriaId
      ? `/gestion/categorias/${categoriaId}/`
      : "/gestion/categorias/",
    {
      method: categoriaId ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    },
  );
}

export interface FiltrosProductos {
  search?: string;
  categoria?: number;
  activo?: "true" | "false";
}

export function listarProductosGestion(
  filtros: FiltrosProductos = {},
): Promise<PaginaApi<ProductoGestion>> {
  const query = queryString({ page_size: 100, ...filtros });
  return getApi<PaginaApi<ProductoGestion>>(`/gestion/productos/?${query}`);
}

export function guardarProducto(
  payload: ProductoPayload,
  productoId?: number,
): Promise<ProductoGestion> {
  return apiRequest<ProductoGestion>(
    productoId ? `/gestion/productos/${productoId}/` : "/gestion/productos/",
    {
      method: productoId ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function listarImagenesProducto(
  productoId: number,
): Promise<PaginaApi<ImagenProductoGestion>> {
  return getApi<PaginaApi<ImagenProductoGestion>>(
    `/gestion/imagenes-producto/?producto=${productoId}&page_size=100`,
  );
}

export function subirImagenProducto(
  productoId: number,
  archivo: File,
  textoAlt: string,
  principal: boolean,
): Promise<ImagenProductoGestion> {
  const formData = new FormData();
  formData.set("producto", String(productoId));
  formData.set("imagen", archivo);
  formData.set("texto_alt", textoAlt);
  formData.set("principal", String(principal));
  formData.set("activa", "true");
  return apiRequest<ImagenProductoGestion>("/gestion/imagenes-producto/", {
    method: "POST",
    body: formData,
  });
}

export function actualizarImagenProducto(
  imagenId: number,
  payload: Partial<Pick<ImagenProductoGestion, "texto_alt" | "principal" | "orden" | "activa">>,
): Promise<ImagenProductoGestion> {
  return apiRequest<ImagenProductoGestion>(
    `/gestion/imagenes-producto/${imagenId}/`,
    { method: "PATCH", body: JSON.stringify(payload) },
  );
}

export function eliminarImagenProducto(imagenId: number): Promise<void> {
  return apiRequest<void>(`/gestion/imagenes-producto/${imagenId}/`, {
    method: "DELETE",
  });
}
