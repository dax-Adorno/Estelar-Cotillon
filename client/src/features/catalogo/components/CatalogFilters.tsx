import type { Categoria } from "../types";

interface CatalogFiltersProps {
  categorias: Categoria[];
  categoriaSeleccionada: string;
  soloDestacados: boolean;
  onCategoriaChange: (categoriaId: string) => void;
  onSoloDestacadosChange: (soloDestacados: boolean) => void;
}

export function CatalogFilters({
  categorias,
  categoriaSeleccionada,
  soloDestacados,
  onCategoriaChange,
  onSoloDestacadosChange,
}: CatalogFiltersProps) {
  return (
    <section className="mt-10 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
      <div className="grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
        <div>
          <label
            className="text-sm font-semibold text-slate-700"
            htmlFor="categoria"
          >
            Filtrar por categoría
          </label>

          <select
            className="mt-2 w-full rounded-xl border border-orange-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-orange-500 focus:ring-2 focus:ring-orange-200"
            id="categoria"
            onChange={(event) => onCategoriaChange(event.target.value)}
            value={categoriaSeleccionada}
          >
            <option value="todas">Todas las categorías</option>

            {categorias.map((categoria) => (
              <option key={categoria.id} value={categoria.id}>
                {categoria.nombre}
              </option>
            ))}
          </select>
        </div>

        <label
          className="flex cursor-pointer items-center gap-3 rounded-xl border border-orange-200 px-4 py-3 font-semibold text-slate-700"
          htmlFor="solo-destacados"
        >
          <input
            checked={soloDestacados}
            className="h-5 w-5 accent-orange-600"
            id="solo-destacados"
            onChange={(event) => onSoloDestacadosChange(event.target.checked)}
            type="checkbox"
          />
          Solo destacados
        </label>
      </div>
    </section>
  );
}
