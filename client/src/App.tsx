import { useEffect, useMemo, useState, type CSSProperties } from "react";
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

function cargarCarritoGuardado(): CarritoItem[] {
  try {
    const guardado = window.localStorage.getItem("estelart-carrito");
    return guardado ? (JSON.parse(guardado) as CarritoItem[]) : [];
  } catch {
    return [];
  }
}

function App() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [promociones, setPromociones] = useState<Promocion[]>([]);
  const [carritoItems, setCarritoItems] = useState<CarritoItem[]>(cargarCarritoGuardado);
  const [pedidoCreado, setPedidoCreado] =
    useState<PedidoPublicoResponse | null>(null);
  const [errorPedido, setErrorPedido] = useState<string | null>(null);
  const [enviandoPedido, setEnviandoPedido] = useState(false);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState("todas");
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
    window.localStorage.setItem("estelart-carrito", JSON.stringify(carritoItems));
  }, [carritoItems]);

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

      return coincideCategoria && producto.destacado && coincideBusqueda;
    });
  }, [categoriaSeleccionada, productos, terminoBusqueda]);

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

  if (window.location.pathname.endsWith("/carrito")) {
    return (
      <main className="min-h-screen bg-[#f7f2e9] text-[#20201f]">
        <header className="border-b border-black/8 bg-white/90 backdrop-blur-xl">
          <div className="mx-auto flex h-20 max-w-6xl items-center justify-between px-5">
            <a href="/" aria-label="Volver a la tienda"><img alt="ESTELART" className="h-11 w-auto" src="/brand/estelart-logo.svg" /></a>
            <a className="rounded-full border border-black/15 px-5 py-2.5 text-sm font-bold transition hover:bg-[#35261f] hover:text-white" href="/">← Seguir comprando</a>
          </div>
        </header>
        <section className="mx-auto max-w-6xl px-5 py-10 sm:py-16">
          <div className="mb-10">
            <p className="text-xs font-black uppercase tracking-[0.2em] text-[#c41d85]">Tu selección</p>
            <h1 className="mt-3 font-serif text-4xl text-[#35261f] sm:text-6xl">Carrito y pedido</h1>
            <p className="mt-3 max-w-xl text-black/55">Revisá tus productos y completá los datos para registrar el pedido.</p>
          </div>
          <div className="grid gap-7 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
            <CartSummary items={carritoItems} onDisminuirProducto={disminuirProductoCarrito} onIncrementarProducto={incrementarProductoCarrito} onQuitarProducto={quitarProductoCarrito} />
            <CheckoutPedido enviandoPedido={enviandoPedido} errorPedido={errorPedido} items={carritoItems} onEnviarPedido={enviarPedido} pedidoCreado={pedidoCreado} />
          </div>
        </section>
      </main>
    );
  }

return (
  <main className="cosmic-store min-h-screen text-[#20201f]">
    <BrandCursor />
    <div className="border-b border-white/10 bg-[#35261f] px-4 py-2.5 text-center text-[11px] font-bold uppercase tracking-[0.16em] text-[#f6efe5]">
      Envíos a todo el país · Compras minoristas y mayoristas
    </div>
    <nav className="cosmic-nav sticky top-0 z-40 px-4">
      <div className="mx-auto flex h-20 max-w-[1600px] items-center justify-between gap-6">
        <a aria-label="Ir al inicio" href="#inicio">
          <img alt="ESTELART" className="nav-logo h-16 w-auto" src="/brand/estelart-logo.svg" />
        </a>
        <div className="cosmic-nav-links hidden items-center gap-10 md:flex">
          <a className="cosmic-nav-link" href="#catalogo">Productos</a>
          <a className="cosmic-nav-link" href="#promociones">Promociones</a>
          <a className="cosmic-nav-link" href="#acceso">Mayoristas</a>
        </div>
        <a className="cosmic-cart rounded-full px-6 py-3 text-base font-black text-white" href="/carrito">
          Carrito · {carritoItems.reduce((total, item) => total + item.cantidad, 0)}
        </a>
      </div>
    </nav>
    <section className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 sm:py-10" id="inicio">
      <header className="pixel-hero mb-8 overflow-hidden rounded-[2rem]" aria-label="ESTELART">
        <div className="pixel-grid" aria-hidden="true" />
        <div className="pixel-burst" aria-hidden="true">
          {Array.from({ length: 48 }, (_, index) => {
            const colors = ["#c41d85", "#ffba1f", "#ff6515", "#1d883f", "#ffffff"];
            return (
              <i
                className="pixel-particle"
                key={index}
                style={{
                  left: `${(index * 37 + 7) % 100}%`,
                  top: `${(index * 53 + 11) % 100}%`,
                  animationDelay: `${(index % 12) * -0.23}s`,
                  animationDuration: `${2.8 + (index % 7) * 0.32}s`,
                  "--pixel-color": colors[index % colors.length],
                  "--pixel-size": `${4 + (index % 5) * 3}px`,
                } as CSSProperties}
              />
            );
          })}
        </div>
        <div className="pixel-orbit pixel-orbit-one" aria-hidden="true" />
        <div className="pixel-orbit pixel-orbit-two" aria-hidden="true" />
        <div className="relative z-10 flex min-h-[620px] flex-col items-center justify-center px-6 py-16 text-center">
          <div className="logo-aura" aria-hidden="true" />
          <img
            alt="Logo ESTELART animado"
            className="hero-logo relative z-10 h-auto w-[min(78vw,620px)]"
            src="/brand/estelart-logo.svg"
          />
          <p className="hero-signature relative z-10 mt-2 text-xs font-black uppercase tracking-[0.32em] text-[#35261f]/60 sm:text-sm">
            Celebrá · Creá · Sorprendé
          </p>
          <a className="hero-scroll relative z-10 mt-12" href="#catalogo" aria-label="Ver productos">
            <span>Ver productos</span><b aria-hidden="true">↓</b>
          </a>
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
            <section className="mt-8 rounded-xl bg-white p-5 shadow-sm ring-1 ring-[#FFBA1F]/40">
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
                  Descubrí nuestra selección especial, filtrá por categoría y guardá
                  tus favoritos en el carrito para completar el pedido en el siguiente paso.
                </p>
              </div>

              <CatalogFilters
                categoriaSeleccionada={categoriaSeleccionada}
                categorias={categorias}
                onCategoriaChange={setCategoriaSeleccionada}
                onTerminoBusquedaChange={setTerminoBusqueda}
                terminoBusqueda={terminoBusqueda}
              />
            </section>

            <div className={`mt-8 grid gap-8 ${usuario?.rol === "admin" ? "xl:grid-cols-[220px_minmax(0,1fr)]" : "grid-cols-1"}`}>
              {usuario?.rol === "admin" && <aside className="hidden xl:block">
              <div className="liquid-card sticky top-6 rounded-xl bg-white p-5 shadow-sm ring-1 ring-[#FFBA1F]/40">
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
                      href="/carrito"
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
            </aside>}
              <section id="catalogo">
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <p className="text-sm font-bold uppercase tracking-wide text-[#7ee79c]">
                      Selección ESTELART
                    </p>
                    <h2 className="mt-1 text-3xl font-black text-white">
                      Productos destacados
                    </h2>
                  </div>

                  {terminoBusqueda.trim().length > 0 && <div className="rounded-lg bg-white px-5 py-3 text-right shadow-sm ring-1 ring-[#FFBA1F]/40" role="status">
                    <p className="text-xs font-bold uppercase text-[#3B3B3B]/60">
                      Resultados
                    </p>
                    <p className="text-2xl font-black text-[#FF6515]">
                      {productosFiltrados.length}
                    </p>
                  </div>}
                </div>

                {productosFiltrados.length === 0 ? (
                  <p className="mt-6 rounded-xl bg-white p-4 text-slate-600 shadow-sm ring-1 ring-[#FFBA1F]/40">
                    No hay productos para los filtros seleccionados.
                  </p>
                ) : (
                  <div className="featured-universe mt-6 grid gap-7 p-5 sm:p-7 md:grid-cols-2 xl:grid-cols-3">
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

            </div>

      {promocionesVigentes.length > 0 && (
        <section className="mt-10" id="promociones">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm font-bold uppercase tracking-wide text-[#ff77c7]">
                Campañas comerciales
              </p>
              <h2 className="mt-1 text-3xl font-black text-white">
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
          className="liquid-card mt-10 rounded-xl bg-white p-6 shadow-sm ring-1 ring-[#FFBA1F]/40"
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
      <footer className="mt-14 border-t border-black/10 bg-[#20201f] text-white">
        <div className="mx-auto grid max-w-[1600px] gap-10 px-6 py-12 md:grid-cols-[1.3fr_0.7fr_0.7fr]">
          <div>
            <img alt="" className="h-12 w-auto brightness-0 invert" src="/brand/estelart-logo.svg" />
            <p className="mt-5 max-w-sm text-sm leading-6 text-white/60">
              Todo para tu fiesta y tus proyectos creativos, con atención cercana y compras simples.
            </p>
            <div className="mt-6 flex gap-3" aria-label="Redes sociales">
              {[
                ["Instagram", "https://instagram.com"],
                ["Facebook", "https://facebook.com"],
                ["TikTok", "https://tiktok.com"],
              ].map(([nombre, url]) => (
                <a
                  aria-label={`Visitar ${nombre}`}
                  className="grid h-11 w-11 place-items-center rounded-full border border-white/20 text-sm font-black transition hover:border-[#ffba1f] hover:bg-[#ffba1f] hover:text-[#20201f]"
                  href={url}
                  key={nombre}
                  rel="noreferrer"
                  target="_blank"
                >
                  {nombre.slice(0, 2)}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-white/45">Tienda</p>
            <div className="mt-5 grid gap-3 text-sm text-white/75">
              <a className="hover:text-white" href="#catalogo">Productos</a>
              <a className="hover:text-white" href="#promociones">Promociones</a>
              <a className="hover:text-white" href="#checkout">Mi carrito</a>
            </div>
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-white/45">Ayuda</p>
            <div className="mt-5 grid gap-3 text-sm text-white/75">
              <a className="hover:text-white" href="#acceso">Cuenta mayorista</a>
              <a className="hover:text-white" href="mailto:ventas@estelart.com">Contacto</a>
              <span>Atención Lun–Sáb</span>
            </div>
          </div>
        </div>
        <div className="border-t border-white/10 px-6 py-5 text-center text-xs text-white/40">
          © {new Date().getFullYear()} ESTELART. Todos los derechos reservados.
        </div>
      </footer>
      <a
        aria-label="Contactar por WhatsApp"
        className="fixed bottom-5 right-5 z-50 flex items-center gap-2 rounded-full bg-[#25d366] px-5 py-3 text-sm font-black text-white shadow-xl transition hover:-translate-y-0.5 hover:bg-[#1fbd5a]"
        href="https://wa.me/"
        rel="noreferrer"
        target="_blank"
      >
        <span aria-hidden="true">●</span> WhatsApp
      </a>
    </main>
  );
}

export default App;
