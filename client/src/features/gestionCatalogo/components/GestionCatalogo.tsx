import { useEffect, useState } from "react";

import { cerrarSesion, obtenerSesionActual } from "../../auth/authApi";
import type { UsuarioActual } from "../../auth/types";
import {
  guardarCategoria,
  guardarProducto,
  listarCategoriasGestion,
  listarProductosGestion,
} from "../gestionCatalogoApi";
import type {
  CategoriaGestion,
  CategoriaPayload,
  ProductoGestion,
  ProductoPayload,
} from "../types";
import { FormularioCategoria } from "./FormularioCategoria";
import { FormularioProducto } from "./FormularioProducto";
import { GestorImagenes } from "./GestorImagenes";

type Seccion = "productos" | "categorias";

function MensajeAcceso({ children, titulo }: { children: React.ReactNode; titulo: string }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#FFEEDC] px-6 py-12 text-[#3B3B3B]">
      <section className="w-full max-w-xl rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-[#FFBA1F]/40">
        <img alt="ESTELART" className="mx-auto h-14 w-auto" src="/brand/estelart-logo.svg" />
        <h1 className="mt-6 text-3xl font-black">{titulo}</h1>
        <div className="mt-4 text-[#3B3B3B]/70">{children}</div>
      </section>
    </main>
  );
}

function obtenerMensaje(error: unknown, alternativo: string): string {
  return error instanceof Error ? error.message : alternativo;
}

export function GestionCatalogo() {
  const [usuario, setUsuario] = useState<UsuarioActual | null>(null);
  const [categorias, setCategorias] = useState<CategoriaGestion[]>([]);
  const [productos, setProductos] = useState<ProductoGestion[]>([]);
  const [seccion, setSeccion] = useState<Seccion>("productos");
  const [categoriaEditada, setCategoriaEditada] = useState<CategoriaGestion | null>(null);
  const [productoEditado, setProductoEditado] = useState<ProductoGestion | null>(null);
  const [productoGaleria, setProductoGaleria] = useState<ProductoGestion | null>(null);
  const [busqueda, setBusqueda] = useState("");
  const [categoriaFiltro, setCategoriaFiltro] = useState("");
  const [estadoFiltro, setEstadoFiltro] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);

  async function cargarCatalogo(filtros = { busqueda, categoriaFiltro, estadoFiltro }) {
    const [paginaCategorias, paginaProductos] = await Promise.all([
      listarCategoriasGestion(),
      listarProductosGestion({
        search: filtros.busqueda.trim() || undefined,
        categoria: filtros.categoriaFiltro ? Number(filtros.categoriaFiltro) : undefined,
        activo: filtros.estadoFiltro === "activos" ? "true" : filtros.estadoFiltro === "inactivos" ? "false" : undefined,
      }),
    ]);
    setCategorias(paginaCategorias.results);
    setProductos(paginaProductos.results);
    setProductoGaleria((actual) => actual ? paginaProductos.results.find((producto) => producto.id === actual.id) ?? null : null);
  }

  useEffect(() => {
    let activo = true;
    async function iniciar() {
      setCargando(true);
      try {
        const sesion = await obtenerSesionActual();
        if (!activo) return;
        setUsuario(sesion);
        if (sesion && ["operador", "admin"].includes(sesion.rol)) {
          const [paginaCategorias, paginaProductos] = await Promise.all([
            listarCategoriasGestion(),
            listarProductosGestion(),
          ]);
          if (activo) {
            setCategorias(paginaCategorias.results);
            setProductos(paginaProductos.results);
          }
        }
      } catch (unknownError) {
        if (activo) setError(obtenerMensaje(unknownError, "No se pudo cargar la gestión del catálogo."));
      } finally {
        if (activo) setCargando(false);
      }
    }
    void iniciar();
    return () => { activo = false; };
  }, []);

  async function aplicarFiltros() {
    setCargando(true);
    setError(null);
    try {
      await cargarCatalogo();
    } catch (unknownError) {
      setError(obtenerMensaje(unknownError, "No se pudieron aplicar los filtros."));
    } finally {
      setCargando(false);
    }
  }

  async function persistirCategoria(payload: CategoriaPayload) {
    setGuardando(true);
    setError(null);
    setMensaje(null);
    try {
      await guardarCategoria(payload, categoriaEditada?.id);
      setMensaje(categoriaEditada ? "Categoría actualizada correctamente." : "Categoría creada correctamente.");
      setCategoriaEditada(null);
      await cargarCatalogo();
    } catch (unknownError) {
      setError(obtenerMensaje(unknownError, "No se pudo guardar la categoría."));
    } finally {
      setGuardando(false);
    }
  }

  async function persistirProducto(payload: ProductoPayload) {
    setGuardando(true);
    setError(null);
    setMensaje(null);
    try {
      await guardarProducto(payload, productoEditado?.id);
      setMensaje(productoEditado ? "Producto actualizado correctamente." : "Producto creado correctamente.");
      setProductoEditado(null);
      await cargarCatalogo();
    } catch (unknownError) {
      setError(obtenerMensaje(unknownError, "No se pudo guardar el producto."));
    } finally {
      setGuardando(false);
    }
  }

  async function salir() {
    await cerrarSesion();
    window.location.assign("/#acceso");
  }

  if (cargando && !usuario) return <MensajeAcceso titulo="Preparando catálogo"><p role="status">Validando permisos y cargando productos...</p></MensajeAcceso>;
  if (!usuario) return <MensajeAcceso titulo="Inicia sesión para continuar"><p>Esta herramienta está reservada para el equipo interno.</p><a className="mt-6 inline-flex rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white" href="/#acceso">Ir al acceso</a></MensajeAcceso>;
  if (!["operador", "admin"].includes(usuario.rol)) return <MensajeAcceso titulo="Acceso operativo restringido"><p>Tu cuenta no posee permisos para administrar el catálogo.</p><a className="mt-6 inline-flex rounded-xl border border-[#3B3B3B]/20 px-5 py-3 font-black" href="/">Volver a la tienda</a></MensajeAcceso>;

  return (
    <main className="min-h-screen bg-[#F8F1E8] text-[#3B3B3B]">
      <header className="border-b border-[#3B3B3B]/10 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <div className="flex items-center gap-4">
            <img alt="ESTELART" className="h-11 w-auto" src="/brand/estelart-logo.svg" />
            <div><p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Operaciones</p><p className="font-black">Gestión de catálogo</p></div>
          </div>
          <nav aria-label="Navegación operativa" className="flex flex-wrap items-center gap-2 text-sm font-black">
            <a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel">Resumen</a>
            <a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel/pedidos">Pedidos</a>
            <a aria-current="page" className="rounded-xl bg-[#FFEEDC] px-4 py-2" href="/panel/catalogo">Catálogo</a>
            <a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel/clientes">Clientes</a>
            <a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/">Ver tienda</a>
            <button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 hover:bg-[#FFEEDC]" onClick={() => void salir()} type="button">Cerrar sesión</button>
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex flex-wrap items-end justify-between gap-5">
          <div><p className="text-sm font-black uppercase tracking-wider text-[#1D883F]">Inventario y publicación</p><h1 className="mt-2 text-4xl font-black tracking-tight">Catálogo comercial</h1><p className="mt-3 max-w-2xl text-[#3B3B3B]/65">Administra precios, stock, visibilidad, categorías e imágenes desde un solo lugar.</p></div>
          <div className="flex rounded-2xl bg-white p-1 shadow-sm ring-1 ring-black/5" role="tablist" aria-label="Secciones del catálogo">
            {(["productos", "categorias"] as Seccion[]).map((item) => <button aria-selected={seccion === item} className={`rounded-xl px-5 py-3 text-sm font-black capitalize ${seccion === item ? "bg-[#3B3B3B] text-white" : "text-[#3B3B3B]/65"}`} key={item} onClick={() => { setSeccion(item); setError(null); setMensaje(null); }} role="tab" type="button">{item}</button>)}
          </div>
        </div>

        {error && <p className="mt-6 rounded-2xl bg-red-50 p-4 font-bold text-red-700" role="alert">{error}</p>}
        {mensaje && <p className="mt-6 rounded-2xl bg-green-50 p-4 font-bold text-green-800" role="status">{mensaje}</p>}

        {seccion === "productos" ? (
          <div className="mt-8 grid gap-6 xl:grid-cols-[0.95fr_1.35fr]">
            <section className="self-start rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5">
              <p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">{productoEditado ? "Edición" : "Nuevo registro"}</p>
              <h2 className="mt-1 text-2xl font-black">{productoEditado ? productoEditado.nombre : "Crear producto"}</h2>
              <div className="mt-6"><FormularioProducto categorias={categorias} guardando={guardando} key={productoEditado?.id ?? "nuevo"} onCancelar={() => setProductoEditado(null)} onGuardar={persistirProducto} producto={productoEditado} /></div>
            </section>
            <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5">
              <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-black uppercase tracking-wider text-[#1D883F]">Inventario</p><h2 className="mt-1 text-2xl font-black">{productos.length} productos</h2></div></div>
              <form className="mt-5 grid gap-3 rounded-2xl bg-[#F8F1E8] p-4 md:grid-cols-[1fr_auto_auto_auto]" onSubmit={(event) => { event.preventDefault(); void aplicarFiltros(); }}>
                <input aria-label="Buscar productos" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setBusqueda(event.target.value)} placeholder="Nombre o SKU" type="search" value={busqueda} />
                <select aria-label="Filtrar por categoría" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setCategoriaFiltro(event.target.value)} value={categoriaFiltro}><option value="">Todas las categorías</option>{categorias.map((categoria) => <option key={categoria.id} value={categoria.id}>{categoria.nombre}</option>)}</select>
                <select aria-label="Filtrar por estado" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setEstadoFiltro(event.target.value)} value={estadoFiltro}><option value="">Todos</option><option value="activos">Publicados</option><option value="inactivos">Ocultos</option></select>
                <button className="rounded-xl bg-[#3B3B3B] px-5 py-2.5 font-black text-white disabled:opacity-50" disabled={cargando} type="submit">{cargando ? "Buscando..." : "Filtrar"}</button>
              </form>
              <div className="mt-5 grid gap-3">
                {productos.length === 0 ? <p className="rounded-2xl border border-dashed border-[#3B3B3B]/20 p-6 text-center text-[#3B3B3B]/60">No hay productos que coincidan con los filtros.</p> : productos.map((producto) => (
                  <article className="rounded-2xl border border-[#3B3B3B]/10 p-4" key={producto.id}>
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div><div className="flex flex-wrap gap-2"><span className={`rounded-full px-2.5 py-1 text-xs font-black ${producto.activo ? "bg-green-50 text-green-800" : "bg-slate-100 text-slate-600"}`}>{producto.activo ? "Publicado" : "Oculto"}</span>{producto.destacado && <span className="rounded-full bg-[#FFBA1F]/20 px-2.5 py-1 text-xs font-black text-amber-800">Destacado</span>}</div><h3 className="mt-3 text-lg font-black">{producto.nombre}</h3><p className="mt-1 text-xs font-bold text-[#3B3B3B]/50">{producto.sku} · {producto.categoria_nombre}</p></div>
                      <div className="text-right"><p className="text-lg font-black text-[#1D883F]">${Number(producto.precio_minorista).toLocaleString("es-AR")}</p><p className={`mt-1 text-sm font-black ${producto.stock <= 10 ? "text-red-700" : "text-[#3B3B3B]/60"}`}>{producto.stock} unidades</p></div>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2"><button className="rounded-xl bg-[#FFEEDC] px-4 py-2 text-sm font-black" onClick={() => { setProductoEditado(producto); window.scrollTo({ top: 0, behavior: "smooth" }); }} type="button">Editar</button><button className="rounded-xl border border-[#C41D85]/25 px-4 py-2 text-sm font-black text-[#C41D85]" onClick={() => setProductoGaleria((actual) => actual?.id === producto.id ? null : producto)} type="button">{productoGaleria?.id === producto.id ? "Cerrar imágenes" : `Imágenes (${producto.cantidad_imagenes})`}</button></div>
                    {productoGaleria?.id === producto.id && <GestorImagenes key={productoGaleria.id} onCambio={cargarCatalogo} producto={productoGaleria} />}
                  </article>
                ))}
              </div>
            </section>
          </div>
        ) : (
          <div className="mt-8 grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
            <section className="self-start rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5"><p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">{categoriaEditada ? "Edición" : "Nuevo registro"}</p><h2 className="mt-1 text-2xl font-black">{categoriaEditada ? categoriaEditada.nombre : "Crear categoría"}</h2><div className="mt-6"><FormularioCategoria categoria={categoriaEditada} guardando={guardando} key={categoriaEditada?.id ?? "nueva"} onCancelar={() => setCategoriaEditada(null)} onGuardar={persistirCategoria} /></div></section>
            <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5"><p className="text-xs font-black uppercase tracking-wider text-[#1D883F]">Organización</p><h2 className="mt-1 text-2xl font-black">{categorias.length} categorías</h2><div className="mt-5 grid gap-3">{categorias.map((categoria) => <article className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-[#3B3B3B]/10 p-4" key={categoria.id}><div><div className="flex items-center gap-2"><h3 className="font-black">{categoria.nombre}</h3><span className={`rounded-full px-2.5 py-1 text-xs font-black ${categoria.activa ? "bg-green-50 text-green-800" : "bg-slate-100 text-slate-600"}`}>{categoria.activa ? "Visible" : "Oculta"}</span></div><p className="mt-2 max-w-xl text-sm text-[#3B3B3B]/60">{categoria.descripcion || "Sin descripción"}</p></div><button className="rounded-xl bg-[#FFEEDC] px-4 py-2 text-sm font-black" onClick={() => setCategoriaEditada(categoria)} type="button">Editar</button></article>)}</div></section>
          </div>
        )}
      </div>
    </main>
  );
}
