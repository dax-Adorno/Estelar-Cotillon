import { useMemo, useState } from "react";

import { ProductImageZoom } from "./ProductImageZoom";
import type { Producto } from "../types";

interface ProductCardProps {
  producto: Producto;
  onAgregarProducto: (producto: Producto) => void;
}

interface ImagenGaleria {
  id: number;
  displayUrl: string;
  zoomUrl: string;
  alt: string;
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

function obtenerImagenesGaleria(producto: Producto): ImagenGaleria[] {
  const imagenes = producto.imagenes ?? [];

  if (imagenes.length > 0) {
    return [...imagenes]
      .sort((actual, siguiente) => {
        if (actual.principal !== siguiente.principal) {
          return actual.principal ? -1 : 1;
        }

        return actual.orden - siguiente.orden || actual.id - siguiente.id;
      })
      .map((imagen) => ({
        id: imagen.id,
        displayUrl: imagen.thumbnail_url || imagen.imagen_url,
        zoomUrl: imagen.imagen_url || imagen.thumbnail_url,
        alt: imagen.texto_alt || producto.nombre,
      }));
  }

  const displayUrl = producto.thumbnail_principal ?? producto.imagen_principal;
  const zoomUrl = producto.imagen_principal ?? producto.thumbnail_principal;

  if (!displayUrl || !zoomUrl) {
    return [];
  }

  return [
    {
      id: 0,
      displayUrl,
      zoomUrl,
      alt: producto.nombre,
    },
  ];
}

export function ProductCard({
  producto,
  onAgregarProducto,
}: ProductCardProps) {
  const [indiceImagenSeleccionada, setIndiceImagenSeleccionada] = useState(0);
  const stockBajo = producto.stock <= 10;

  const imagenesGaleria = useMemo(
    () => obtenerImagenesGaleria(producto),
    [producto],
  );

  const imagenSeleccionada = imagenesGaleria[indiceImagenSeleccionada] ?? null;

  return (
    <article className="featured-product group flex h-full flex-col overflow-hidden rounded-[10px] border border-white/50 bg-white transition duration-300 hover:-translate-y-2">
      <div className="relative">
        <ProductImageZoom
          alt={imagenSeleccionada?.alt ?? producto.nombre}
          imageUrl={imagenSeleccionada?.displayUrl ?? null}
          zoomUrl={imagenSeleccionada?.zoomUrl ?? null}
        />

        {producto.destacado && (
          <span className="absolute left-4 top-4 rounded-full bg-[#20201f] px-3 py-1 text-[10px] font-black uppercase tracking-[0.12em] text-white shadow-sm">
            Destacado
          </span>
        )}

        <span
          className={
            stockBajo
              ? "absolute bottom-4 right-4 rounded-full bg-red-100 px-3 py-1 text-xs font-black text-red-700"
              : "absolute bottom-4 right-4 rounded-full bg-[#1D883F]/15 px-3 py-1 text-xs font-black text-[#1D883F]"
          }
        >
          Stock: {producto.stock}
        </span>
      </div>

      {imagenesGaleria.length > 1 && (
        <div className="flex gap-2 overflow-x-auto border-b border-[#FFBA1F]/30 bg-white p-3">
          {imagenesGaleria.map((imagen, index) => (
            <button
              aria-label={`Ver imagen ${index + 1} de ${producto.nombre}`}
              className={
                index === indiceImagenSeleccionada
                  ? "h-14 w-14 shrink-0 overflow-hidden rounded-xl ring-2 ring-[#FF6515]"
                  : "h-14 w-14 shrink-0 overflow-hidden rounded-xl ring-1 ring-[#FFBA1F]/60"
              }
              key={imagen.id}
              onClick={() => setIndiceImagenSeleccionada(index)}
              type="button"
            >
              <img
                alt=""
                className="h-full w-full object-cover"
                loading="lazy"
                src={imagen.displayUrl}
              />
            </button>
          ))}
        </div>
      )}

      <div className="flex flex-1 flex-col p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-[#c41d85]">
              {producto.categoria_nombre}
            </p>

            <h3 className="mt-2 text-xl font-extrabold leading-tight text-[#20201f]">
              {producto.nombre}
            </h3>
          </div>
        </div>

        <p className="mt-3 inline-flex w-fit rounded-full bg-[#FFEEDC] px-3 py-1 text-xs font-bold text-[#3B3B3B]/75">
          SKU: {producto.sku}
        </p>

        <p className="mt-4 line-clamp-3 text-sm leading-6 text-[#3B3B3B]/70">
          {producto.descripcion ||
            "Producto disponible para catálogo comercial."}
        </p>

        <div className="mt-6 grid gap-3 rounded-2xl bg-[#f5f2ed] p-4">
          <div className="flex items-end justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-[#3B3B3B]/55">
                Minorista
              </p>
              <p className="text-2xl font-black text-[#20201f]">
                {formatearPrecio(producto.precio_minorista)}
              </p>
            </div>
          </div>

          <div className="rounded-xl bg-white p-3">
            <p className="text-xs font-black uppercase tracking-wide text-[#3B3B3B]/55">
              Mayorista
            </p>
            <p className="text-lg font-black text-[#1D883F]">
              {formatearPrecio(producto.precio_mayorista)}
            </p>
            <p className="text-xs font-semibold text-[#3B3B3B]/60">
              Desde {producto.cantidad_minima_mayorista} unidades
            </p>
          </div>
        </div>

        <button
          className="mt-5 w-full rounded-full bg-[#20201f] px-4 py-3 font-bold text-white transition hover:bg-[#c41d85] focus:outline-none focus:ring-4 focus:ring-[#c41d85]/15"
          onClick={() => onAgregarProducto(producto)}
          type="button"
        >
          Agregar al carrito
        </button>
      </div>
    </article>
  );
}
