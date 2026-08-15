import { useEffect, useState } from "react";

import {
  obtenerCategorias,
  obtenerProductos,
  obtenerPromociones,
} from "./features/catalogo/catalogoApi";
import type {
  Categoria,
  Producto,
  Promocion,
} from "./features/catalogo/types";

function formatearPrecio(valor: string): string {
  return Number(valor).toLocaleString("es-AR", {
    style: "currency",
    currency: "ARS",
  });
}

function App() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [promociones, setPromociones] = useState<Promocion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function cargarCatalogo(): Promise<void> {
      try {
        const [categoriasApi, productosApi, promocionesApi] =
          await Promise.all([
            obtenerCategorias(),
            obtenerProductos(),
            obtenerPromociones(),
          ]);

        setCategorias(categoriasApi);
        setProductos(productosApi);
        setPromociones(promocionesApi);
      } catch {
        setError("No se pudo cargar el catálogo desde la API.");
      } finally {
        setCargando(false);
      }
    }

    void cargarCatalogo();
  }, []);

  return (
    <main className="min-h-screen bg-orange-50 px-6 py-10 text-slate-900">
      <section className="mx-auto max-w-6xl">
        <div className="mb-10 rounded-3xl bg-white p-8 shadow-sm ring-1 ring-orange-100">
          <span className="mb-4 inline-flex rounded-full bg-orange-100 px-4 py-2 text-sm font-semibold text-orange-700">
            ESTELART Platform
          </span>

          <h1 className="max-w-4xl text-4xl font-bold tracking-tight text-slate-950 md:text-6xl">
            Plataforma comercial para cotillón, insumos creativos y clientes
            mayoristas.
          </h1>

          <p className="mt-6 max-w-3xl text-lg text-slate-600">
            Catálogo personalizado, pedidos, promociones, métricas, reportes y
            futura integración con asistente IA.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <a
              className="rounded-xl bg-orange-600 px-5 py-3 font-semibold text-white transition hover:bg-orange-700"
              href="#catalogo"
            >
              Ver catálogo
            </a>

            <a
              className="rounded-xl border border-orange-300 px-5 py-3 font-semibold text-orange-700 transition hover:bg-orange-100"
              href="#mayoristas"
            >
              Acceso mayoristas
            </a>
          </div>
        </div>

        <section className="grid gap-4 md:grid-cols-3">
          <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
            <p className="text-sm font-semibold text-slate-500">Categorías</p>
            <p className="mt-2 text-4xl font-bold">{categorias.length}</p>
          </article>

          <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
            <p className="text-sm font-semibold text-slate-500">Productos</p>
            <p className="mt-2 text-4xl font-bold">{productos.length}</p>
          </article>

          <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
            <p className="text-sm font-semibold text-slate-500">Promociones</p>
            <p className="mt-2 text-4xl font-bold">{promociones.length}</p>
          </article>
        </section>

        {cargando && (
          <p className="mt-8 rounded-xl bg-white p-4 text-slate-600">
            Cargando catálogo...
          </p>
        )}

        {error && (
          <p className="mt-8 rounded-xl bg-red-50 p-4 font-medium text-red-700">
            {error}
          </p>
        )}

        {!cargando && !error && (
          <section id="catalogo" className="mt-10">
            <h2 className="text-2xl font-bold">Catálogo destacado</h2>

            {productos.length === 0 ? (
              <p className="mt-4 rounded-xl bg-white p-4 text-slate-600">
                Todavía no hay productos cargados en la API.
              </p>
            ) : (
              <div className="mt-6 grid gap-4 md:grid-cols-3">
                {productos.slice(0, 6).map((producto) => (
                  <article
                    className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100"
                    key={producto.id}
                  >
                    <p className="text-sm font-semibold text-orange-700">
                      {producto.categoria_nombre}
                    </p>
                    <h3 className="mt-2 text-xl font-bold">
                      {producto.nombre}
                    </h3>
                    <p className="mt-2 text-sm text-slate-500">
                      SKU: {producto.sku}
                    </p>
                    <p className="mt-4 text-lg font-bold">
                      {formatearPrecio(producto.precio_minorista)}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

        {!cargando && !error && promociones.length > 0 && (
          <section className="mt-10">
            <h2 className="text-2xl font-bold">Promociones activas</h2>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {promociones.slice(0, 3).map((promocion) => (
                <article
                  className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100"
                  key={promocion.id}
                >
                  <p className="text-sm font-semibold text-orange-700">
                    {promocion.tipo_promocion}
                  </p>
                  <h3 className="mt-2 text-xl font-bold">{promocion.nombre}</h3>
                  <p className="mt-2 text-sm text-slate-600">
                    {promocion.vigente ? "Vigente" : "No vigente"}
                  </p>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
