import { ProductImageZoom } from "./ProductImageZoom";
import type { Producto } from "../types";

interface ProductCardProps {
  producto: Producto;
}

function formatearPrecio(valor: string): string {
  const numero = Number(valor);

  if (Number.isNaN(numero)) {
    return "$ 0,00";
  }

  return numero.toLocaleString("es-AR", {
    style: "currency",
    currency: "ARS",
  });
}

export function ProductCard({ producto }: ProductCardProps) {
  const stockBajo = producto.stock <= 10;
  const imagenProducto =
    producto.thumbnail_principal ?? producto.imagen_principal;

  return (
    <article className="flex h-full flex-col overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-orange-100">
      <ProductImageZoom imageUrl={imagenProducto} alt={producto.nombre} />

      <div className="flex flex-1 flex-col p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-orange-700">
              {producto.categoria_nombre}
            </p>

            <h3 className="mt-2 text-xl font-bold text-slate-950">
              {producto.nombre}
            </h3>
          </div>

          {producto.destacado && (
            <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-700">
              Destacado
            </span>
          )}
        </div>

        <p className="mt-3 text-sm text-slate-500">SKU: {producto.sku}</p>

        <p className="mt-4 line-clamp-3 text-sm text-slate-600">
          {producto.descripcion ||
            "Producto disponible para catálogo comercial."}
        </p>

        <div className="mt-6 grid gap-3 rounded-xl bg-orange-50 p-4">
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">
              Minorista
            </p>
            <p className="text-lg font-bold text-slate-950">
              {formatearPrecio(producto.precio_minorista)}
            </p>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">
              Mayorista
            </p>
            <p className="text-lg font-bold text-slate-950">
              {formatearPrecio(producto.precio_mayorista)}
            </p>
            <p className="text-xs text-slate-500">
              Desde {producto.cantidad_minima_mayorista} unidades
            </p>
          </div>
        </div>

        <div className="mt-auto pt-5">
          <p
            className={
              stockBajo
                ? "font-semibold text-red-700"
                : "font-semibold text-emerald-700"
            }
          >
            Stock: {producto.stock} unidades
          </p>
        </div>
      </div>
    </article>
  );
}
