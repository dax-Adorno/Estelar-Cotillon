import { useEffect, useState } from "react";

import {
  actualizarImagenProducto,
  eliminarImagenProducto,
  listarImagenesProducto,
  subirImagenProducto,
} from "../gestionCatalogoApi";
import type { ImagenProductoGestion, ProductoGestion } from "../types";

interface GestorImagenesProps {
  producto: ProductoGestion;
  onCambio: () => Promise<void>;
}

export function GestorImagenes({ producto, onCambio }: GestorImagenesProps) {
  const [imagenes, setImagenes] = useState<ImagenProductoGestion[]>([]);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [textoAlt, setTextoAlt] = useState("");
  const [principal, setPrincipal] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState<number | "nueva" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function cargar() {
    setCargando(true);
    setError(null);
    try {
      const pagina = await listarImagenesProducto(producto.id);
      setImagenes(pagina.results);
    } catch (unknownError) {
      setError(unknownError instanceof Error ? unknownError.message : "No se pudieron cargar las imágenes.");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    let activo = true;
    listarImagenesProducto(producto.id)
      .then((pagina) => {
        if (activo) setImagenes(pagina.results);
      })
      .catch((unknownError: unknown) => {
        if (activo) setError(unknownError instanceof Error ? unknownError.message : "No se pudieron cargar las imágenes.");
      })
      .finally(() => {
        if (activo) setCargando(false);
      });
    return () => { activo = false; };
  }, [producto.id]);

  async function ejecutar(imagenId: number, operacion: () => Promise<unknown>) {
    setProcesando(imagenId);
    setError(null);
    try {
      await operacion();
      await Promise.all([cargar(), onCambio()]);
    } catch (unknownError) {
      setError(unknownError instanceof Error ? unknownError.message : "No se pudo actualizar la imagen.");
    } finally {
      setProcesando(null);
    }
  }

  return (
    <section aria-label={`Imágenes de ${producto.nombre}`} className="mt-6 border-t border-[#3B3B3B]/10 pt-6">
      <div>
        <p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Galería del producto</p>
        <h3 className="mt-1 text-xl font-black">{producto.nombre}</h3>
        <p className="mt-1 text-sm text-[#3B3B3B]/60">La imagen principal se muestra primero en la tienda.</p>
      </div>

      {error && <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm font-bold text-red-700" role="alert">{error}</p>}

      <form
        className="mt-5 grid gap-3 rounded-2xl bg-[#F8F1E8] p-4 md:grid-cols-[1fr_1fr_auto] md:items-end"
        onSubmit={async (event) => {
          event.preventDefault();
          if (!archivo) return;
          const formulario = event.currentTarget;
          setProcesando("nueva");
          setError(null);
          try {
            await subirImagenProducto(producto.id, archivo, textoAlt.trim(), principal);
            setArchivo(null);
            setTextoAlt("");
            setPrincipal(false);
            formulario.reset();
            await Promise.all([cargar(), onCambio()]);
          } catch (unknownError) {
            setError(unknownError instanceof Error ? unknownError.message : "No se pudo subir la imagen.");
          } finally {
            setProcesando(null);
          }
        }}
      >
        <label className="grid gap-1.5 text-sm font-bold">
          Archivo de imagen
          <input accept="image/*" className="rounded-xl border border-[#3B3B3B]/15 bg-white p-2" onChange={(event) => setArchivo(event.target.files?.[0] ?? null)} required type="file" />
        </label>
        <label className="grid gap-1.5 text-sm font-bold">
          Texto alternativo
          <input className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2.5" maxLength={180} onChange={(event) => setTextoAlt(event.target.value)} placeholder="Describe la imagen" value={textoAlt} />
        </label>
        <div className="flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-sm font-bold"><input checked={principal} className="h-5 w-5 accent-[#C41D85]" onChange={(event) => setPrincipal(event.target.checked)} type="checkbox" /> Principal</label>
          <button className="rounded-xl bg-[#C41D85] px-4 py-2.5 font-black text-white disabled:opacity-50" disabled={!archivo || procesando !== null} type="submit">{procesando === "nueva" ? "Subiendo..." : "Subir"}</button>
        </div>
      </form>

      {cargando ? (
        <p className="mt-5 text-sm" role="status">Cargando galería...</p>
      ) : imagenes.length === 0 ? (
        <p className="mt-5 rounded-2xl border border-dashed border-[#3B3B3B]/20 p-5 text-sm text-[#3B3B3B]/60">Este producto todavía no tiene imágenes.</p>
      ) : (
        <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {imagenes.map((imagen) => (
            <article className="overflow-hidden rounded-2xl border border-[#3B3B3B]/10 bg-white" key={imagen.id}>
              <div className="aspect-[4/3] bg-[#FFEEDC]">
                <img alt={imagen.texto_alt || producto.nombre} className="h-full w-full object-cover" loading="lazy" src={imagen.thumbnail_url || imagen.imagen_url} />
              </div>
              <div className="p-4">
                <div className="flex flex-wrap gap-2 text-xs font-black">
                  {imagen.principal && <span className="rounded-full bg-[#C41D85]/10 px-2.5 py-1 text-[#C41D85]">Principal</span>}
                  <span className={`rounded-full px-2.5 py-1 ${imagen.activa ? "bg-green-50 text-green-800" : "bg-slate-100 text-slate-600"}`}>{imagen.activa ? "Visible" : "Oculta"}</span>
                </div>
                <p className="mt-3 min-h-5 text-sm text-[#3B3B3B]/65">{imagen.texto_alt || "Sin texto alternativo"}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {!imagen.principal && imagen.activa && <button className="rounded-lg border border-[#C41D85]/30 px-3 py-2 text-xs font-black text-[#C41D85]" disabled={procesando !== null} onClick={() => void ejecutar(imagen.id, () => actualizarImagenProducto(imagen.id, { principal: true }))} type="button">Hacer principal</button>}
                  <button className="rounded-lg border border-[#3B3B3B]/15 px-3 py-2 text-xs font-black" disabled={procesando !== null} onClick={() => void ejecutar(imagen.id, () => actualizarImagenProducto(imagen.id, { activa: !imagen.activa }))} type="button">{imagen.activa ? "Ocultar" : "Activar"}</button>
                  <button className="rounded-lg border border-red-200 px-3 py-2 text-xs font-black text-red-700" disabled={procesando !== null} onClick={() => { if (window.confirm("¿Eliminar esta imagen de forma permanente?")) void ejecutar(imagen.id, () => eliminarImagenProducto(imagen.id)); }} type="button">Eliminar</button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
