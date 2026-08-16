export interface Categoria {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  activa: boolean;
}

export interface ImagenProducto {
  id: number;
  imagen_url: string;
  thumbnail_url: string;
  texto_alt: string;
  principal: boolean;
  orden: number;
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
  imagen_principal: string | null;
  thumbnail_principal: string | null;
  imagenes: ImagenProducto[];
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
