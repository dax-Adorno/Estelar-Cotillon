export interface MetricasComerciales {
  pedidos_total: number;
  pedidos_pendientes: number;
  total_estimado: string;
  unidades_pedidas: number;
  productos_activos: number;
  productos_stock_bajo: number;
  categorias_activas: number;
  promociones_activas: number;
}

export interface ConteoEstadoPedido {
  estado: string;
  cantidad: number;
}

export interface ConteoCanalPedido {
  canal_venta: string;
  cantidad: number;
}

export interface ProductoTop {
  producto_id: number;
  sku: string;
  nombre: string;
  unidades: number;
  importe: string;
}

export interface ProductoStockBajo {
  id: number;
  sku: string;
  nombre: string;
  stock: number;
}

export interface ResumenComercial {
  generado_en: string;
  stock_bajo_umbral: number;
  metricas: MetricasComerciales;
  pedidos_por_estado: ConteoEstadoPedido[];
  pedidos_por_canal: ConteoCanalPedido[];
  top_productos: ProductoTop[];
  productos_stock_bajo: ProductoStockBajo[];
}
