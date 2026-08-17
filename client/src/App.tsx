import { useEffect, useMemo, useState } from "react";

import { CartSummary } from "./features/carrito/components/CartSummary";
import type { CarritoItem } from "./features/carrito/types";
import {
  obtenerCategorias,
  obtenerProductos,
  obtenerPromociones,
} from "./features/catalogo/catalogoApi";
import { CatalogFilters } from "./features/catalogo/components/CatalogFilters";
import { ProductCard } from "./features/catalogo/components/ProductCard";
import type {
  Categoria,
  Producto,
  Promocion,
} from "./features/catalogo/types";

function normalizarTexto(valor: string): string {
  return valor.trim().toLowerCase();
}

function App() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [promociones, setPromociones] = useState<Promocion[]>([]);
  const [carritoItems, setCarritoItems] = useState<CarritoItem[]>([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState("todas");
  const [soloDestacados, setSoloDestacados] = useState(false);
  const [terminoBusqueda, setTerminoBusqueda] = useState("");
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

  const productosFiltrados = useMemo(() => {
    const busqueda = normalizarTexto(terminoBusqueda);

    return productos.filter((producto) => {
      const coincideCategoria =
        categoriaSeleccionada === "todas" ||
        producto.categoria === Number(categoriaSeleccionada);

      const coincideDestacado = !soloDestacados || producto.destacado;

      const textoProducto = normalizarTexto(
        [
          producto.nombre,
          producto.sku,
          producto.descripcion,
          producto.categoria_nombre,
        ].join(" "),
      );

      const coincideBusqueda =
        busqueda.length === 0 || textoProducto.includes(busqueda);

      return coincideCategoria && coincideDestacado && coincideBusqueda;
    });
  }, [categoriaSeleccionada, productos, soloDestacados, terminoBusqueda]);

  const promocionesVigentes = useMemo(() => {
    return promociones.filter(
      (promocion) => promocion.activa && promocion.vigente,
    );
  }, [promociones]);

  function agregarProductoAlCarrito(producto: Producto): void {
    setCarritoItems((itemsActuales) => {
      const itemExistente = itemsActuales.find(
        (item) => item.producto.id === producto.id,
      );

      if (itemExistente) {
        return itemsActuales.map((item) =>
          item.producto.id === producto.id
            ? {
                ...item,
                cantidad: item.cantidad + 1,
              }
            : item,
        );
      }

      return [
        ...itemsActuales,
        {
          producto,
          cantidad: 1,
        },
      ];
    });
  }

  return (
    <main className="min-h-screen bg-orange-50 px-6 py-10 text-slate-900">
      <section className="mx-auto max-w-6xl">
        <header className="mb-10 rounded-3xl bg-white p-8 shadow-sm ring-1 ring-orange-100">
          <span className="mb-4 inline-flex rounded-full bg-orange-100 px-4 py-2 text-sm font-semibold text-orange-700">
            ESTELART Platform
          </span>

          <h1 className="max-w-4xl text-4xl font-bold tracking-tight text-slate-950 md:text-6xl">
            Catálogo inteligente para cotillón, insumos creativos y clientes
            mayoristas.
          </h1>

          <p className="mt-6 max-w-3xl text-lg text-slate-600">
            Productos, categorías, precios mayoristas, promociones y stock en una
            misma plataforma comercial.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
            <p className="text-sm font-semibold text-slate-500">Categorías</p>
            <p className="mt-2 text-4xl font-bold">{categorias.length}</p>
          </article>

          <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
            <p className="text-sm font-semibold text-slate-500">Productos</p>
            <p className="mt-2 text-4xl font-bold">{productos.length}</p>
          </article>

          <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
            <p className="text-sm font-semibold text-slate-500">Filtrados</p>
            <p className="mt-2 text-4xl font-bold">
              {productosFiltrados.length}
            </p>
          </article>

          <article className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
            <p className="text-sm font-semibold text-slate-500">Promociones</p>
            <p className="mt-2 text-4xl font-bold">
              {promocionesVigentes.length}
            </p>
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
          <>
            <CatalogFilters
              categoriaSeleccionada={categoriaSeleccionada}
              categorias={categorias}
              onCategoriaChange={setCategoriaSeleccionada}
              onSoloDestacadosChange={setSoloDestacados}
              onTerminoBusquedaChange={setTerminoBusqueda}
              soloDestacados={soloDestacados}
              terminoBusqueda={terminoBusqueda}
            />

            <section className="mt-10" id="catalogo">
              <h2 className="text-2xl font-bold">Catálogo comercial</h2>

              {productosFiltrados.length === 0 ? (
                <p className="mt-6 rounded-xl bg-white p-4 text-slate-600">
                  No hay productos para los filtros seleccionados.
                </p>
              ) : (
                <div className="mt-6 grid gap-4 md:grid-cols-3">
                  {productosFiltrados.map((producto) => (
                    <ProductCard
                      key={producto.id}
                      onAgregarProducto={agregarProductoAlCarrito}
                      producto={producto}
                    />
                  ))}
                </div>
              )}
            </section>

            <CartSummary items={carritoItems} />

            {promocionesVigentes.length > 0 && (
              <section className="mt-10" id="promociones">
                <h2 className="text-2xl font-bold">Promociones activas</h2>

                <div className="mt-6 grid gap-4 md:grid-cols-3">
                  {promocionesVigentes.map((promocion) => (
                    <article
                      className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100"
                      key={promocion.id}
                    >
                      <p className="text-sm font-semibold text-orange-700">
                        {promocion.tipo_promocion}
                      </p>

                      <h3 className="mt-2 text-xl font-bold">
                        {promocion.nombre}
                      </h3>

                      <p className="mt-2 text-sm text-slate-600">
                        {promocion.descripcion ||
                          "Promoción vigente para el canal comercial seleccionado."}
                      </p>

                      <p className="mt-4 text-sm font-semibold text-emerald-700">
                        Vigente
                      </p>
                    </article>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </section>
    </main>
  );
}

export default App;
