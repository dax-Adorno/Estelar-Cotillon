import { useEffect, useMemo, useState } from "react";
import { BrandCursor } from "./components/BrandCursor";
import { obtenerSesionActual } from "./features/auth/authApi";
import { AccesoCuenta } from "./features/auth/components/AccesoCuenta";
import type { UsuarioActual } from "./features/auth/types";
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
import { CheckoutPedido } from "./features/pedidos/components/CheckoutPedido";
import {
  construirPedidoPublicoPayload,
  crearPedidoPublico,
} from "./features/pedidos/pedidosApi";
import type {
  DatosPedidoCliente,
  PedidoPublicoResponse,
} from "./features/pedidos/types";

function normalizarTexto(valor: string): string {
  return valor.trim().toLowerCase();
}

function App() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [promociones, setPromociones] = useState<Promocion[]>([]);
  const [carritoItems, setCarritoItems] = useState<CarritoItem[]>([]);
  const [pedidoCreado, setPedidoCreado] =
    useState<PedidoPublicoResponse | null>(null);
  const [errorPedido, setErrorPedido] = useState<string | null>(null);
  const [enviandoPedido, setEnviandoPedido] = useState(false);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState("todas");
  const [soloDestacados, setSoloDestacados] = useState(false);
  const [terminoBusqueda, setTerminoBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usuario, setUsuario] = useState<UsuarioActual | null>(null);
  const [cargandoSesion, setCargandoSesion] = useState(true);

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

  useEffect(() => {
    obtenerSesionActual()
      .then(setUsuario)
      .catch(() => setUsuario(null))
      .finally(() => setCargandoSesion(false));
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

  function limpiarEstadoPedido(): void {
    setPedidoCreado(null);
    setErrorPedido(null);
  }

  function agregarProductoAlCarrito(producto: Producto): void {
    limpiarEstadoPedido();

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

  function incrementarProductoCarrito(productoId: number): void {
    limpiarEstadoPedido();

    setCarritoItems((itemsActuales) =>
      itemsActuales.map((item) =>
        item.producto.id === productoId
          ? {
              ...item,
              cantidad: item.cantidad + 1,
            }
          : item,
      ),
    );
  }

  function disminuirProductoCarrito(productoId: number): void {
    limpiarEstadoPedido();

    setCarritoItems((itemsActuales) =>
      itemsActuales
        .map((item) =>
          item.producto.id === productoId
            ? {
                ...item,
                cantidad: item.cantidad - 1,
              }
            : item,
        )
        .filter((item) => item.cantidad > 0),
    );
  }

  function quitarProductoCarrito(productoId: number): void {
    limpiarEstadoPedido();

    setCarritoItems((itemsActuales) =>
      itemsActuales.filter((item) => item.producto.id !== productoId),
    );
  }

  async function enviarPedido(datosCliente: DatosPedidoCliente): Promise<void> {
    if (carritoItems.length === 0) {
      setErrorPedido("El carrito está vacío.");
      return;
    }

    setEnviandoPedido(true);
    setErrorPedido(null);
    setPedidoCreado(null);

    try {
      const payload = construirPedidoPublicoPayload(
        datosCliente,
        carritoItems,
      );
      const pedido = await crearPedidoPublico(payload);

      setPedidoCreado(pedido);
      setCarritoItems([]);
    } catch (unknownError) {
      const mensaje =
        unknownError instanceof Error
          ? unknownError.message
          : "No se pudo crear el pedido.";

      setErrorPedido(mensaje);
    } finally {
      setEnviandoPedido(false);
    }
  }

return (
  <main className="min-h-screen bg-[#FFEEDC] px-6 py-8 text-[#3B3B3B]">
    <BrandCursor/>
    <section className="mx-auto max-w-7xl">
      <header className="mb-8 overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-[#FFBA1F]/40">
        <div className="flex flex-col gap-8 p-6 md:grid md:grid-cols-[1.15fr_0.85fr] md:p-8">
          <div>
            <div className="flex flex-wrap items-center gap-4">
              <img
                alt="ESTELART"
                className="h-16 w-auto"
                src="/brand/estelart-logo.svg"
              />

              <span className="rounded-full bg-[#FFBA1F]/20 px-4 py-2 text-sm font-bold text-[#3B3B3B]">
                Plataforma comercial
              </span>
            </div>

            <h1 className="mt-8 max-w-4xl text-4xl font-black tracking-tight text-[#3B3B3B] md:text-6xl">
              Catálogo inteligente para cotillón, insumos creativos y pedidos
              mayoristas.
            </h1>

            <p className="mt-6 max-w-3xl text-lg text-[#3B3B3B]/75">
              ESTELART centraliza productos, precios, stock, promociones,
              carrito, pedidos y gestión operativa en una sola plataforma para
              vender con más orden.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <a
                className="rounded-xl bg-[#FF6515] px-5 py-3 font-bold text-white shadow-sm transition hover:opacity-90"
                href="#catalogo"
              >
                Ver catálogo
              </a>

              <a
                className="rounded-xl border border-[#C41D85]/30 bg-white px-5 py-3 font-bold text-[#C41D85] transition hover:bg-[#C41D85]/10"
                href="#checkout"
              >
                Crear pedido
              </a>
              <a
                className="rounded-xl border border-[#1D883F]/30 bg-white px-5 py-3 font-bold text-[#1D883F] transition hover:bg-[#1D883F]/10"
                href="#acceso"
              >
                {usuario ? `Hola, ${usuario.nombre || "cuenta"}` : "Ingresar"}
              </a>

              <a
                className="rounded-xl bg-[#C41D85] px-5 py-3 font-bold text-white shadow-sm transition hover:opacity-90"
                href="#acceso"
              >
                Registro mayorista
              </a>
            </div>
          </div>

          <div className="relative min-h-72 overflow-hidden rounded-3xl bg-[#FFBA1F]/20">
            <img
              alt="Insumos creativos ESTELART"
              className="h-full min-h-72 w-full object-cover"
              src="/brand/estelar-imagen.jpeg"
            />

            <div className="absolute bottom-4 left-4 right-4 rounded-2xl bg-white/90 p-4 shadow-sm backdrop-blur">
              <p className="text-sm font-bold text-[#1D883F]">
                Sistema real para gestión comercial
              </p>
              <p className="mt-1 text-sm text-[#3B3B3B]/75">
                Catálogo, carrito, pedidos, panel operativo y reportes.
              </p>
            </div>
          </div>
        </div>
      </header>
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
            <section className="mt-8 rounded-3xl bg-white p-5 shadow-sm ring-1 ring-[#FFBA1F]/40">
              <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-bold uppercase tracking-wide text-[#C41D85]">
                    Marketplace operativo
                </p>
                <h2 className="mt-1 text-2xl font-black text-[#3B3B3B]">
                  Buscar, filtrar y armar pedidos
                </h2>
                </div>

                <p className="max-w-xl text-sm text-[#3B3B3B]/70">
                  Estructura pensada para venta real: búsqueda rápida, filtros,
                  productos visibles, carrito persistente y creación de pedido desde el
                  mismo flujo.
                </p>
              </div>

              <CatalogFilters
                categoriaSeleccionada={categoriaSeleccionada}
                categorias={categorias}
                onCategoriaChange={setCategoriaSeleccionada}
                onSoloDestacadosChange={setSoloDestacados}
                onTerminoBusquedaChange={setTerminoBusqueda}
                soloDestacados={soloDestacados}
                terminoBusqueda={terminoBusqueda}
              />
            </section>

            <div className="mt-8 grid gap-8 xl:grid-cols-[250px_minmax(0,1fr)_420px]">
              <aside className="hidden xl:block">
              <div className="liquid-card sticky top-6 rounded-3xl bg-white p-5 shadow-sm ring-1 ring-[#FFBA1F]/40">
                <div className="relative">
                  <p className="text-sm font-black uppercase tracking-wide text-[#C41D85]">
                    Menú
                  </p>

                  <nav className="mt-5 grid gap-2 text-sm font-bold text-[#3B3B3B]">
                    <a
                      className="rounded-2xl bg-[#FFEEDC] px-4 py-3 transition hover:bg-[#FFBA1F]/30"
                      href="#catalogo"
                    >
                      Catálogo
                    </a>
                    <a
                      className="rounded-2xl px-4 py-3 transition hover:bg-[#FFBA1F]/20"
                      href="#promociones"
                    >
                      Promociones
                    </a>
                    <a
                      className="rounded-2xl px-4 py-3 transition hover:bg-[#FFBA1F]/20"
                      href="#checkout"
                    >
                      Pedido en curso
                    </a>
                    <a
                      className="rounded-2xl px-4 py-3 transition hover:bg-[#FFBA1F]/20"
                      href="#acceso"
                    >
                      Mayoristas
                    </a>
                  </nav>

                  <div className="mt-6 rounded-2xl bg-white/80 p-4">
                    <p className="text-xs font-black uppercase text-[#3B3B3B]/55">
                      Acceso privado
                    </p>
                    <p className="mt-2 text-sm text-[#3B3B3B]/70">
                      Acceso real para clientes mayoristas, operadores y administradores.
                    </p>
                  </div>
                </div>
              </div>
            </aside>
              <section id="catalogo">
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <p className="text-sm font-bold uppercase tracking-wide text-[#1D883F]">
                      Catálogo
                    </p>
                    <h2 className="mt-1 text-3xl font-black text-[#3B3B3B]">
                      Productos disponibles
                    </h2>
                  </div>

                  <div className="rounded-2xl bg-white px-5 py-3 text-right shadow-sm ring-1 ring-[#FFBA1F]/40">
                    <p className="text-xs font-bold uppercase text-[#3B3B3B]/60">
                      Resultados
                    </p>
                    <p className="text-2xl font-black text-[#FF6515]">
                      {productosFiltrados.length}
                    </p>
                  </div>
                </div>

                {productosFiltrados.length === 0 ? (
                  <p className="mt-6 rounded-xl bg-white p-4 text-slate-600 shadow-sm ring-1 ring-[#FFBA1F]/40">
                    No hay productos para los filtros seleccionados.
                  </p>
                ) : (
                  <div className="mt-6 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
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

              <aside className="lg:sticky lg:top-6 lg:self-start">
                <div className="rounded-3xl bg-white p-4 shadow-sm ring-1 ring-[#FFBA1F]/40">
                  <div className="mb-4 rounded-2xl bg-[#FFEEDC] p-4">
                    <p className="text-sm font-bold uppercase tracking-wide text-[#C41D85]">
                      Pedido en curso
                    </p>
                    <h2 className="mt-1 text-2xl font-black text-[#3B3B3B]">
                      Carrito y datos del cliente
                    </h2>
                    <p className="mt-2 text-sm text-[#3B3B3B]/70">
                      El pedido se arma desde el catálogo y se envía al backend para
                      gestión operativa.
                    </p>
                  </div>

                  <CartSummary
                    items={carritoItems}
                    onDisminuirProducto={disminuirProductoCarrito}
                    onIncrementarProducto={incrementarProductoCarrito}
                    onQuitarProducto={quitarProductoCarrito}
                  />

                  <div id="checkout">
                    <CheckoutPedido
                      enviandoPedido={enviandoPedido}
                      errorPedido={errorPedido}
                      items={carritoItems}
                      onEnviarPedido={enviarPedido}
                      pedidoCreado={pedidoCreado}
                    />
                  </div>
                </div>
              </aside>
            </div>

      {promocionesVigentes.length > 0 && (
        <section className="mt-10" id="promociones">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm font-bold uppercase tracking-wide text-[#C41D85]">
                Campañas comerciales
              </p>
              <h2 className="mt-1 text-3xl font-black text-[#3B3B3B]">
                Promociones activas
              </h2>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {promocionesVigentes.map((promocion) => (
              <article
                className="promo-pulse rounded-2xl bg-white p-6 shadow-sm ring-1 ring-[#FF6515]/40"
                key={promocion.id}
              >
                <p className="text-sm font-bold text-[#C41D85]">
                  {promocion.tipo_promocion}
                </p>

                <h3 className="mt-2 text-xl font-black text-[#3B3B3B]">
                  {promocion.nombre}
                </h3>

                <p className="mt-2 text-sm text-[#3B3B3B]/70">
                  {promocion.descripcion ||
                    "Promoción vigente para el canal comercial seleccionado."}
                </p>

                <p className="mt-4 text-sm font-bold text-[#1D883F]">
                  Vigente
                </p>
              </article>
            ))}
          </div>
        </section>
      )}
        <section
          className="liquid-card mt-10 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-[#FFBA1F]/40"
          id="acceso"
        >
          <div className="relative grid gap-6 md:grid-cols-[1fr_1fr]">
            <div>
              <p className="text-sm font-black uppercase tracking-wide text-[#C41D85]">
                Acceso ESTELART
              </p>
              <h2 className="mt-2 text-3xl font-black text-[#3B3B3B]">
                Tu cuenta ESTELART
              </h2>
              <p className="mt-3 text-[#3B3B3B]/70">
                Inicia sesión o solicita una cuenta mayorista. El acceso utiliza
                sesión segura, protección CSRF y permisos definidos por el backend.
              </p>
            </div>

            <AccesoCuenta
              cargandoSesion={cargandoSesion}
              onSesionChange={setUsuario}
              usuario={usuario}
            />
          </div>
        </section>
  </>
)}
      </section>
    </main>
  );
}

export default App;
