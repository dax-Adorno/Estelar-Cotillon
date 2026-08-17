import type { Producto } from "../catalogo/types";

export interface CarritoItem {
  producto: Producto;
  cantidad: number;
}
