import { useEffect, useState } from "react";

import { cerrarSesion, obtenerSesionActual } from "../../auth/authApi";
import type { UsuarioActual } from "../../auth/types";
import { ETIQUETAS_ESTADO, ETIQUETAS_PAGO } from "../etiquetas";
import { listarPedidos, obtenerPedido } from "../gestionPedidosApi";
import type { CanalVenta, EstadoPago, EstadoPedido, FiltrosPedidos, PedidoDetalle, PedidoResumen } from "../types";
import { DetallePedidoPanel } from "./DetallePedidoPanel";

const ETIQUETAS_CANAL: Record<CanalVenta, string> = {
  web: "Tienda web",
  whatsapp: "WhatsApp",
  instagram: "Instagram",
  mercado_libre: "Mercado Libre",
  tienda_nube: "Tienda Nube",
  presencial: "Presencial",
};

function importe(valor: string): string {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(valor));
}

function fecha(valor: string): string {
  return new Intl.DateTimeFormat("es-AR", { dateStyle: "short", timeStyle: "short" }).format(new Date(valor));
}

function MensajeAcceso({ children, titulo }: { children: React.ReactNode; titulo: string }) {
  return <main className="flex min-h-screen items-center justify-center bg-[#FFEEDC] px-6 py-12 text-[#3B3B3B]"><section className="w-full max-w-xl rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-[#FFBA1F]/40"><img alt="ESTELART" className="mx-auto h-14 w-auto" src="/brand/estelart-logo.svg" /><h1 className="mt-6 text-3xl font-black">{titulo}</h1><div className="mt-4 text-[#3B3B3B]/70">{children}</div></section></main>;
}

export function GestionPedidos() {
  const busquedaInicial = new URLSearchParams(window.location.search).get("search") ?? "";
  const [usuario, setUsuario] = useState<UsuarioActual | null>(null);
  const [pedidos, setPedidos] = useState<PedidoResumen[]>([]);
  const [total, setTotal] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [detalle, setDetalle] = useState<PedidoDetalle | null>(null);
  const [busqueda, setBusqueda] = useState(busquedaInicial);
  const [estado, setEstado] = useState<EstadoPedido | "">("");
  const [estadoPago, setEstadoPago] = useState<EstadoPago | "">("");
  const [canal, setCanal] = useState<CanalVenta | "">("");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [orden, setOrden] = useState<FiltrosPedidos["ordering"]>("-creado_en");
  const [cargando, setCargando] = useState(true);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function filtrosActuales(numeroPagina = pagina): FiltrosPedidos {
    return {
      search: busqueda.trim() || undefined,
      estado: estado || undefined,
      estado_pago: estadoPago || undefined,
      canal_venta: canal || undefined,
      desde: desde || undefined,
      hasta: hasta || undefined,
      ordering: orden,
      page: numeroPagina,
    };
  }

  async function cargar(filtros: FiltrosPedidos) {
    const resultado = await listarPedidos(filtros);
    setPedidos(resultado.results);
    setTotal(resultado.count);
  }

  useEffect(() => {
    let activo = true;
    async function iniciar() {
      try {
        const sesion = await obtenerSesionActual();
        if (!activo) return;
        setUsuario(sesion);
        if (sesion && ["operador", "admin"].includes(sesion.rol)) {
          const resultado = await listarPedidos({ search: busquedaInicial || undefined, ordering: "-creado_en", page: 1 });
          if (activo) { setPedidos(resultado.results); setTotal(resultado.count); }
        }
      } catch (unknownError) {
        if (activo) setError(unknownError instanceof Error ? unknownError.message : "No se pudieron cargar los pedidos.");
      } finally {
        if (activo) setCargando(false);
      }
    }
    void iniciar();
    return () => { activo = false; };
  }, [busquedaInicial]);

  async function aplicarFiltros(nuevaPagina = 1) {
    setCargando(true);
    setError(null);
    try {
      await cargar(filtrosActuales(nuevaPagina));
      setPagina(nuevaPagina);
      setDetalle(null);
    } catch (unknownError) {
      setError(unknownError instanceof Error ? unknownError.message : "No se pudieron aplicar los filtros.");
    } finally {
      setCargando(false);
    }
  }

  async function abrirDetalle(pedidoId: number) {
    setCargandoDetalle(true);
    setError(null);
    try {
      setDetalle(await obtenerPedido(pedidoId));
    } catch (unknownError) {
      setError(unknownError instanceof Error ? unknownError.message : "No se pudo abrir el pedido.");
    } finally {
      setCargandoDetalle(false);
    }
  }

  async function actualizarDetalle(actualizado: PedidoDetalle) {
    setDetalle(actualizado);
    await cargar(filtrosActuales());
  }

  async function salir() {
    await cerrarSesion();
    window.location.assign("/#acceso");
  }

  if (cargando && !usuario) return <MensajeAcceso titulo="Preparando gestión de pedidos"><p role="status">Validando permisos y cargando operaciones...</p></MensajeAcceso>;
  if (!usuario) return <MensajeAcceso titulo="Inicia sesión para continuar"><p>Esta herramienta está reservada para el equipo interno.</p><a className="mt-6 inline-flex rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white" href="/#acceso">Ir al acceso</a></MensajeAcceso>;
  if (!["operador", "admin"].includes(usuario.rol)) return <MensajeAcceso titulo="Acceso operativo restringido"><p>Tu cuenta no posee permisos para gestionar pedidos.</p><a className="mt-6 inline-flex rounded-xl border border-[#3B3B3B]/20 px-5 py-3 font-black" href="/">Volver a la tienda</a></MensajeAcceso>;

  const resumenSeleccionado = detalle ? pedidos.find((pedido) => pedido.id === detalle.id) : null;
  const paginas = Math.max(Math.ceil(total / 25), 1);

  return (
    <main className="min-h-screen bg-[#F8F1E8] text-[#3B3B3B]">
      <header className="border-b border-[#3B3B3B]/10 bg-white"><div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4"><div className="flex items-center gap-4"><img alt="ESTELART" className="h-11 w-auto" src="/brand/estelart-logo.svg" /><div><p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Operaciones</p><p className="font-black">Gestión de pedidos</p></div></div><nav aria-label="Navegación operativa" className="flex flex-wrap items-center gap-2 text-sm font-black"><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel">Resumen</a><a className="rounded-xl bg-[#FFEEDC] px-4 py-2" href="/panel/pedidos" aria-current="page">Pedidos</a><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel/catalogo">Catálogo</a><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel/clientes">Clientes</a><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/">Ver tienda</a><button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 hover:bg-[#FFEEDC]" onClick={() => void salir()} type="button">Cerrar sesión</button></nav></div></header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div><p className="text-sm font-black uppercase tracking-wider text-[#1D883F]">Seguimiento comercial</p><h1 className="mt-2 text-4xl font-black tracking-tight">Pedidos y cobros</h1><p className="mt-3 max-w-2xl text-[#3B3B3B]/65">Consulta cada venta, controla su preparación, registra cobros y conserva un historial auditable.</p></div>
        {error && <p className="mt-6 rounded-2xl bg-red-50 p-4 font-bold text-red-700" role="alert">{error}</p>}

        <section className="mt-8 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5">
          <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Bandeja operativa</p><h2 className="mt-1 text-2xl font-black">{total} {total === 1 ? "pedido" : "pedidos"}</h2></div><p className="rounded-full bg-[#F8F1E8] px-4 py-2 text-xs font-black">Página {pagina} de {paginas}</p></div>
          <form className="mt-5 grid gap-3 rounded-2xl bg-[#F8F1E8] p-4 md:grid-cols-2 xl:grid-cols-4" onSubmit={(event) => { event.preventDefault(); void aplicarFiltros(); }}>
            <input aria-label="Buscar pedidos" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setBusqueda(event.target.value)} placeholder="Código, cliente, email o WhatsApp" type="search" value={busqueda} />
            <select aria-label="Filtrar por estado del pedido" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setEstado(event.target.value as EstadoPedido | "")} value={estado}><option value="">Todos los estados</option>{Object.entries(ETIQUETAS_ESTADO).map(([valor, etiqueta]) => <option key={valor} value={valor}>{etiqueta}</option>)}</select>
            <select aria-label="Filtrar por estado del pago" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setEstadoPago(event.target.value as EstadoPago | "")} value={estadoPago}><option value="">Todos los pagos</option>{Object.entries(ETIQUETAS_PAGO).map(([valor, etiqueta]) => <option key={valor} value={valor}>{etiqueta}</option>)}</select>
            <select aria-label="Filtrar por canal" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setCanal(event.target.value as CanalVenta | "")} value={canal}><option value="">Todos los canales</option>{Object.entries(ETIQUETAS_CANAL).map(([valor, etiqueta]) => <option key={valor} value={valor}>{etiqueta}</option>)}</select>
            <label className="grid gap-1 text-xs font-black">Desde<input className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5 text-sm" onChange={(event) => setDesde(event.target.value)} type="date" value={desde} /></label>
            <label className="grid gap-1 text-xs font-black">Hasta<input className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5 text-sm" min={desde || undefined} onChange={(event) => setHasta(event.target.value)} type="date" value={hasta} /></label>
            <select aria-label="Ordenar pedidos" className="self-end rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setOrden(event.target.value as FiltrosPedidos["ordering"])} value={orden}><option value="-creado_en">Más recientes</option><option value="creado_en">Más antiguos</option><option value="-total">Mayor importe</option><option value="total">Menor importe</option></select>
            <button className="self-end rounded-xl bg-[#3B3B3B] px-5 py-2.5 font-black text-white disabled:opacity-50" disabled={cargando} type="submit">{cargando ? "Consultando..." : "Aplicar filtros"}</button>
          </form>

          <div className="mt-5 grid gap-3">
            {pedidos.length === 0 ? <p className="rounded-2xl border border-dashed border-[#3B3B3B]/20 p-6 text-center text-[#3B3B3B]/60">No hay pedidos que coincidan con los filtros.</p> : pedidos.map((pedido) => <article className={`rounded-2xl border p-4 ${detalle?.id === pedido.id ? "border-[#C41D85] bg-[#C41D85]/5" : "border-[#3B3B3B]/10"}`} key={pedido.id}><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex flex-wrap gap-2"><span className="rounded-full bg-[#1D883F]/10 px-2.5 py-1 text-xs font-black text-[#1D883F]">{ETIQUETAS_ESTADO[pedido.estado]}</span><span className="rounded-full bg-[#C41D85]/10 px-2.5 py-1 text-xs font-black text-[#C41D85]">{ETIQUETAS_PAGO[pedido.estado_pago]}</span><span className="rounded-full bg-[#FFEEDC] px-2.5 py-1 text-xs font-black">{ETIQUETAS_CANAL[pedido.canal_venta]}</span></div><h3 className="mt-3 text-lg font-black">{pedido.codigo}</h3><p className="mt-1 text-sm font-bold text-[#3B3B3B]/65">{pedido.cliente_nombre}</p><p className="mt-1 text-xs text-[#3B3B3B]/50">{pedido.cliente_email}</p></div><div className="text-right"><p className="text-xl font-black text-[#1D883F]">{importe(pedido.total)}</p><p className="mt-1 text-xs font-bold text-[#3B3B3B]/50">{pedido.cantidad_unidades} {pedido.cantidad_unidades === 1 ? "unidad" : "unidades"} · {pedido.cantidad_items} {pedido.cantidad_items === 1 ? "producto" : "productos"}</p><p className="mt-2 text-xs text-[#3B3B3B]/50">{fecha(pedido.creado_en)}</p></div></div><button className="mt-4 rounded-xl bg-[#FFEEDC] px-4 py-2 text-sm font-black disabled:opacity-50" disabled={cargandoDetalle} onClick={() => void abrirDetalle(pedido.id)} type="button">{cargandoDetalle ? "Abriendo..." : "Ver y gestionar"}</button></article>)}
          </div>
          <div className="mt-5 flex items-center justify-between gap-4"><button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 text-sm font-black disabled:opacity-40" disabled={pagina <= 1 || cargando} onClick={() => void aplicarFiltros(pagina - 1)} type="button">Anterior</button><button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 text-sm font-black disabled:opacity-40" disabled={pagina >= paginas || cargando} onClick={() => void aplicarFiltros(pagina + 1)} type="button">Siguiente</button></div>
        </section>

        {detalle && resumenSeleccionado && <div className="mt-6"><DetallePedidoPanel detalle={detalle} key={`${detalle.id}-${detalle.estado}-${detalle.estado_pago}`} onActualizar={actualizarDetalle} onCerrar={() => setDetalle(null)} resumen={resumenSeleccionado} /></div>}
      </div>
    </main>
  );
}
