import { useState } from "react";

import type { CategoriaGestion, CategoriaPayload } from "../types";

interface FormularioCategoriaProps {
  categoria: CategoriaGestion | null;
  guardando: boolean;
  onCancelar: () => void;
  onGuardar: (payload: CategoriaPayload) => Promise<void>;
}

export function FormularioCategoria({
  categoria,
  guardando,
  onCancelar,
  onGuardar,
}: FormularioCategoriaProps) {
  const [nombre, setNombre] = useState(categoria?.nombre ?? "");
  const [descripcion, setDescripcion] = useState(categoria?.descripcion ?? "");
  const [activa, setActiva] = useState(categoria?.activa ?? true);

  return (
    <form
      className="grid gap-4"
      onSubmit={(event) => {
        event.preventDefault();
        void onGuardar({ nombre: nombre.trim(), descripcion: descripcion.trim(), activa });
      }}
    >
      <label className="grid gap-1.5 text-sm font-bold">
        Nombre
        <input
          className="rounded-xl border border-[#3B3B3B]/20 px-4 py-3 outline-none focus:border-[#C41D85]"
          maxLength={120}
          onChange={(event) => setNombre(event.target.value)}
          required
          value={nombre}
        />
      </label>
      <label className="grid gap-1.5 text-sm font-bold">
        Descripción
        <textarea
          className="min-h-24 rounded-xl border border-[#3B3B3B]/20 px-4 py-3 outline-none focus:border-[#C41D85]"
          maxLength={1000}
          onChange={(event) => setDescripcion(event.target.value)}
          value={descripcion}
        />
      </label>
      <label className="flex items-center gap-3 text-sm font-bold">
        <input
          checked={activa}
          className="h-5 w-5 accent-[#1D883F]"
          onChange={(event) => setActiva(event.target.checked)}
          type="checkbox"
        />
        Visible para el catálogo
      </label>
      <div className="flex flex-wrap gap-3 pt-2">
        <button
          className="rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white disabled:opacity-50"
          disabled={guardando}
          type="submit"
        >
          {guardando ? "Guardando..." : categoria ? "Actualizar categoría" : "Crear categoría"}
        </button>
        {categoria && (
          <button
            className="rounded-xl border border-[#3B3B3B]/20 px-5 py-3 font-black"
            onClick={onCancelar}
            type="button"
          >
            Cancelar edición
          </button>
        )}
      </div>
    </form>
  );
}
