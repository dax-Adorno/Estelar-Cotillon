import type { Categoria } from "../types";

interface CatalogFiltersProps {
  categorias: Categoria[];
  categoriaSeleccionada: string;
  terminoBusqueda: string;
  onCategoriaChange: (categoriaId: string) => void;
  onTerminoBusquedaChange: (terminoBusqueda: string) => void;
}

export function CatalogFilters({
  categorias,
  categoriaSeleccionada,
  terminoBusqueda,
  onCategoriaChange,
  onTerminoBusquedaChange,
}: CatalogFiltersProps) {
  return (
    <section className="rounded-2xl bg-[#f5f2ed] p-4 sm:p-5">
      <div className="grid gap-4 md:grid-cols-2 md:items-end">
        <div>
          <label
            className="text-sm font-semibold text-slate-700"
            htmlFor="busqueda-producto"
          >
            Buscar producto
          </label>

          <input
            className="mt-2 w-full rounded-xl border border-black/10 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-[#c41d85] focus:ring-2 focus:ring-[#c41d85]/10"
            id="busqueda-producto"
            onChange={(event) => onTerminoBusquedaChange(event.target.value)}
            placeholder="Nombre, SKU, descripción o categoría"
            type="search"
            value={terminoBusqueda}
          />
        </div>

        <div>
          <label
            className="text-sm font-semibold text-slate-700"
            htmlFor="categoria"
          >
            Filtrar por categoría
          </label>

          <select
            className="mt-2 w-full rounded-xl border border-black/10 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-[#c41d85] focus:ring-2 focus:ring-[#c41d85]/10"
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

      </div>
    </section>
  );
}
