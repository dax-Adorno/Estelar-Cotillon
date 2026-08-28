export interface PaginaApi<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CategoriaGestion {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  activa: boolean;
  creada_en: string;
  actualizada_en: string;
}

export interface ProductoGestion {
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
  cantidad_imagenes: number;
  creado_en: string;
  actualizado_en: string;
}

export interface ImagenProductoGestion {
  id: number;
  producto: number;
  producto_sku: string;
  imagen_url: string;
  thumbnail_url: string;
  texto_alt: string;
  principal: boolean;
  orden: number;
  activa: boolean;
  creada_en: string;
  actualizada_en: string;
}

export interface CategoriaPayload {
  nombre: string;
  descripcion: string;
  activa: boolean;
}

export interface ProductoPayload {
  categoria: number;
  sku: string;
  nombre: string;
  descripcion: string;
  precio_minorista: string;
  precio_mayorista: string;
  cantidad_minima_mayorista: number;
  stock: number;
  activo: boolean;
  destacado: boolean;
}
