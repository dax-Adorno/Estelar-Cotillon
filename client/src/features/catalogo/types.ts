export interface Categoria {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  activa: boolean;
}

export interface Producto {
  id: number;
  categoria: number;
  categoria_nombre: string;
  sku: string;
  nombre: string;
  slug: string;
  descripcion: string;
  precio_minorista: string;
  precio_mayorista: string;
  cantidad_minima_mayorista: number;
  stock: number;
  activo: boolean;
  destacado: boolean;
}

export interface Promocion {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  tipo_promocion: string;
  porcentaje_descuento: string | null;
  monto_descuento: string | null;
  compra_minima: string | null;
  canal_venta: string;
  activa: boolean;
  vigente: boolean;
}
