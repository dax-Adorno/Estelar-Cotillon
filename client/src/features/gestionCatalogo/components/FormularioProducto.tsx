import { useState } from "react";

import type { CategoriaGestion, ProductoGestion, ProductoPayload } from "../types";

interface FormularioProductoProps {
  categorias: CategoriaGestion[];
  guardando: boolean;
  producto: ProductoGestion | null;
  onCancelar: () => void;
  onGuardar: (payload: ProductoPayload) => Promise<void>;
}

const VACIO = {
  categoria: "",
  sku: "",
  nombre: "",
  descripcion: "",
  precioMinorista: "",
  precioMayorista: "",
  minimoMayorista: "1",
  stock: "0",
  activo: true,
  destacado: false,
};

export function FormularioProducto({
  categorias,
  guardando,
  producto,
  onCancelar,
  onGuardar,
}: FormularioProductoProps) {
  const [formulario, setFormulario] = useState(() =>
    producto
      ? {
          categoria: String(producto.categoria),
          sku: producto.sku,
          nombre: producto.nombre,
          descripcion: producto.descripcion,
          precioMinorista: producto.precio_minorista,
          precioMayorista: producto.precio_mayorista,
          minimoMayorista: String(producto.cantidad_minima_mayorista),
          stock: String(producto.stock),
          activo: producto.activo,
          destacado: producto.destacado,
        }
      : { ...VACIO, categoria: categorias[0] ? String(categorias[0].id) : "" },
  );

  function cambiar(campo: keyof typeof formulario, valor: string | boolean) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }));
  }

  return (
    <form
      className="grid gap-4 sm:grid-cols-2"
      onSubmit={(event) => {
        event.preventDefault();
        void onGuardar({
          categoria: Number(formulario.categoria),
          sku: formulario.sku.trim(),
          nombre: formulario.nombre.trim(),
          descripcion: formulario.descripcion.trim(),
          precio_minorista: formulario.precioMinorista,
          precio_mayorista: formulario.precioMayorista,
          cantidad_minima_mayorista: Number(formulario.minimoMayorista),
          stock: Number(formulario.stock),
          activo: formulario.activo,
          destacado: formulario.destacado,
        });
      }}
    >
      <label className="grid gap-1.5 text-sm font-bold">
        Categoría
        <select
          className="rounded-xl border border-[#3B3B3B]/20 bg-white px-4 py-3"
          onChange={(event) => cambiar("categoria", event.target.value)}
          required
          value={formulario.categoria}
        >
          <option value="">Seleccionar</option>
          {categorias.filter((categoria) => categoria.activa || categoria.id === producto?.categoria).map((categoria) => (
            <option key={categoria.id} value={categoria.id}>{categoria.nombre}</option>
          ))}
        </select>
      </label>
      <label className="grid gap-1.5 text-sm font-bold">
        SKU
        <input className="rounded-xl border border-[#3B3B3B]/20 px-4 py-3" maxLength={64} onChange={(event) => cambiar("sku", event.target.value)} required value={formulario.sku} />
      </label>
      <label className="grid gap-1.5 text-sm font-bold sm:col-span-2">
        Nombre
        <input className="rounded-xl border border-[#3B3B3B]/20 px-4 py-3" maxLength={180} onChange={(event) => cambiar("nombre", event.target.value)} required value={formulario.nombre} />
      </label>
      <label className="grid gap-1.5 text-sm font-bold sm:col-span-2">
        Descripción
        <textarea className="min-h-24 rounded-xl border border-[#3B3B3B]/20 px-4 py-3" onChange={(event) => cambiar("descripcion", event.target.value)} value={formulario.descripcion} />
      </label>
      <label className="grid gap-1.5 text-sm font-bold">
        Precio minorista
        <input className="rounded-xl border border-[#3B3B3B]/20 px-4 py-3" min="0.01" onChange={(event) => cambiar("precioMinorista", event.target.value)} required step="0.01" type="number" value={formulario.precioMinorista} />
      </label>
      <label className="grid gap-1.5 text-sm font-bold">
        Precio mayorista
        <input className="rounded-xl border border-[#3B3B3B]/20 px-4 py-3" min="0.01" onChange={(event) => cambiar("precioMayorista", event.target.value)} required step="0.01" type="number" value={formulario.precioMayorista} />
      </label>
      <label className="grid gap-1.5 text-sm font-bold">
        Compra mínima mayorista
        <input className="rounded-xl border border-[#3B3B3B]/20 px-4 py-3" min="1" onChange={(event) => cambiar("minimoMayorista", event.target.value)} required type="number" value={formulario.minimoMayorista} />
      </label>
      <label className="grid gap-1.5 text-sm font-bold">
        Stock disponible
        <input className="rounded-xl border border-[#3B3B3B]/20 px-4 py-3" min="0" onChange={(event) => cambiar("stock", event.target.value)} required type="number" value={formulario.stock} />
      </label>
      <div className="flex flex-wrap gap-6 sm:col-span-2">
        <label className="flex items-center gap-3 text-sm font-bold">
          <input checked={formulario.activo} className="h-5 w-5 accent-[#1D883F]" onChange={(event) => cambiar("activo", event.target.checked)} type="checkbox" /> Publicado
        </label>
        <label className="flex items-center gap-3 text-sm font-bold">
          <input checked={formulario.destacado} className="h-5 w-5 accent-[#C41D85]" onChange={(event) => cambiar("destacado", event.target.checked)} type="checkbox" /> Destacado
        </label>
      </div>
      <div className="flex flex-wrap gap-3 pt-2 sm:col-span-2">
        <button className="rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white disabled:opacity-50" disabled={guardando || categorias.length === 0} type="submit">
          {guardando ? "Guardando..." : producto ? "Actualizar producto" : "Crear producto"}
        </button>
        {producto && <button className="rounded-xl border border-[#3B3B3B]/20 px-5 py-3 font-black" onClick={onCancelar} type="button">Cancelar edición</button>}
      </div>
    </form>
  );
}
