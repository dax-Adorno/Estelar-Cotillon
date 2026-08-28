import { useEffect, useState } from "react";

import { cerrarSesion, obtenerSesionActual } from "../../auth/authApi";
import type { RolUsuario, UsuarioActual } from "../../auth/types";
import { actualizarPerfil, listarClientes } from "../gestionClientesApi";
import type { ClienteGestion, EstadoCuenta, FiltrosClientes, TipoCliente } from "../types";

const ETIQUETAS_ROL: Record<RolUsuario, string> = {
  cliente_minorista: "Cliente minorista",
  cliente_mayorista: "Cliente mayorista",
  operador: "Operador",
  admin: "Administrador",
};

function importe(valor: string): string {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(valor));
}

function fecha(valor: string | null): string {
  if (!valor) return "Sin compras";
  return new Intl.DateTimeFormat("es-AR", { dateStyle: "short", timeStyle: "short" }).format(new Date(valor));
}

function MensajeAcceso({ children, titulo }: { children: React.ReactNode; titulo: string }) {
  return <main className="flex min-h-screen items-center justify-center bg-[#FFEEDC] px-6 py-12 text-[#3B3B3B]"><section className="w-full max-w-xl rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-[#FFBA1F]/40"><img alt="ESTELART" className="mx-auto h-14 w-auto" src="/brand/estelart-logo.svg" /><h1 className="mt-6 text-3xl font-black">{titulo}</h1><div className="mt-4 text-[#3B3B3B]/70">{children}</div></section></main>;
}

function etiquetaCuenta(cliente: ClienteGestion): string {
  if (!cliente.rol) return "Sin cuenta web";
  if (cliente.rol === "cliente_mayorista") return cliente.mayorista_aprobado ? "Mayorista aprobado" : "Mayorista pendiente";
  return ETIQUETAS_ROL[cliente.rol];
}

export function GestionClientes() {
  const [usuario, setUsuario] = useState<UsuarioActual | null>(null);
  const [clientes, setClientes] = useState<ClienteGestion[]>([]);
  const [seleccionado, setSeleccionado] = useState<ClienteGestion | null>(null);
  const [total, setTotal] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [busqueda, setBusqueda] = useState("");
  const [tipo, setTipo] = useState<TipoCliente | "">("");
  const [cuenta, setCuenta] = useState<EstadoCuenta | "">("");
  const [orden, setOrden] = useState<FiltrosClientes["ordering"]>("nombre");
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);

  function filtros(numeroPagina = pagina): FiltrosClientes {
    return { search: busqueda.trim() || undefined, tipo_cliente: tipo || undefined, cuenta: cuenta || undefined, ordering: orden, page: numeroPagina };
  }

  async function cargar(parametros: FiltrosClientes) {
    const resultado = await listarClientes(parametros);
    setClientes(resultado.results);
    setTotal(resultado.count);
    setSeleccionado((actual) => actual ? resultado.results.find((cliente) => cliente.id === actual.id) ?? null : null);
  }

  useEffect(() => {
    let activo = true;
    async function iniciar() {
      try {
        const sesion = await obtenerSesionActual();
        if (!activo) return;
        setUsuario(sesion);
        if (sesion && ["operador", "admin"].includes(sesion.rol)) {
          const resultado = await listarClientes({ ordering: "nombre", page: 1 });
          if (activo) { setClientes(resultado.results); setTotal(resultado.count); }
        }
      } catch (unknownError) {
        if (activo) setError(unknownError instanceof Error ? unknownError.message : "No se pudo cargar la cartera de clientes.");
      } finally {
        if (activo) setCargando(false);
      }
    }
    void iniciar();
    return () => { activo = false; };
  }, []);

  async function aplicarFiltros(nuevaPagina = 1) {
    setCargando(true); setError(null); setMensaje(null);
    try { await cargar(filtros(nuevaPagina)); setPagina(nuevaPagina); }
    catch (unknownError) { setError(unknownError instanceof Error ? unknownError.message : "No se pudieron aplicar los filtros."); }
    finally { setCargando(false); }
  }

  async function cambiarPerfil(payload: { rol?: "cliente_minorista" | "cliente_mayorista" | "operador"; mayorista_aprobado?: boolean }) {
    if (!seleccionado?.perfil_id) return;
    setProcesando(true); setError(null); setMensaje(null);
    try {
      await actualizarPerfil(seleccionado.perfil_id, payload);
      await cargar(filtros());
      setMensaje("Perfil y permisos actualizados correctamente.");
    } catch (unknownError) {
      setError(unknownError instanceof Error ? unknownError.message : "No se pudo actualizar el perfil.");
    } finally { setProcesando(false); }
  }

  async function salir() { await cerrarSesion(); window.location.assign("/#acceso"); }

  if (cargando && !usuario) return <MensajeAcceso titulo="Preparando cartera comercial"><p role="status">Validando permisos y cargando clientes...</p></MensajeAcceso>;
  if (!usuario) return <MensajeAcceso titulo="Inicia sesión para continuar"><p>Esta herramienta está reservada para el equipo interno.</p><a className="mt-6 inline-flex rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white" href="/#acceso">Ir al acceso</a></MensajeAcceso>;
  if (!["operador", "admin"].includes(usuario.rol)) return <MensajeAcceso titulo="Acceso operativo restringido"><p>Tu cuenta no posee permisos para consultar clientes.</p><a className="mt-6 inline-flex rounded-xl border border-[#3B3B3B]/20 px-5 py-3 font-black" href="/">Volver a la tienda</a></MensajeAcceso>;

  const paginas = Math.max(Math.ceil(total / 25), 1);
  return <main className="min-h-screen bg-[#F8F1E8] text-[#3B3B3B]">
    <header className="border-b border-[#3B3B3B]/10 bg-white"><div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4"><div className="flex items-center gap-4"><img alt="ESTELART" className="h-11 w-auto" src="/brand/estelart-logo.svg" /><div><p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Operaciones</p><p className="font-black">Gestión de clientes</p></div></div><nav aria-label="Navegación operativa" className="flex flex-wrap items-center gap-2 text-sm font-black"><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel">Resumen</a><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel/pedidos">Pedidos</a><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel/catalogo">Catálogo</a><a aria-current="page" className="rounded-xl bg-[#FFEEDC] px-4 py-2" href="/panel/clientes">Clientes</a><a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/">Ver tienda</a><button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2" onClick={() => void salir()} type="button">Cerrar sesión</button></nav></div></header>
    <div className="mx-auto max-w-7xl px-6 py-8"><div><p className="text-sm font-black uppercase tracking-wider text-[#1D883F]">Relación comercial</p><h1 className="mt-2 text-4xl font-black tracking-tight">Clientes y mayoristas</h1><p className="mt-3 max-w-2xl text-[#3B3B3B]/65">Segmenta la cartera, revisa actividad y administra aprobaciones comerciales con permisos controlados.</p></div>
      {error && <p className="mt-6 rounded-2xl bg-red-50 p-4 font-bold text-red-700" role="alert">{error}</p>}{mensaje && <p className="mt-6 rounded-2xl bg-green-50 p-4 font-bold text-green-800" role="status">{mensaje}</p>}
      <div className="mt-8 grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5"><div className="flex flex-wrap justify-between gap-3"><div><p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Cartera activa</p><h2 className="mt-1 text-2xl font-black">{total} {total === 1 ? "cliente" : "clientes"}</h2></div><p className="self-start rounded-full bg-[#F8F1E8] px-4 py-2 text-xs font-black">Página {pagina} de {paginas}</p></div>
          <form className="mt-5 grid gap-3 rounded-2xl bg-[#F8F1E8] p-4 md:grid-cols-2" onSubmit={(event) => { event.preventDefault(); void aplicarFiltros(); }}><input aria-label="Buscar clientes" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setBusqueda(event.target.value)} placeholder="Nombre, empresa, email, WhatsApp o CUIT" type="search" value={busqueda} /><select aria-label="Filtrar por tipo de cliente" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setTipo(event.target.value as TipoCliente | "")} value={tipo}><option value="">Minoristas y mayoristas</option><option value="minorista">Minoristas</option><option value="mayorista">Mayoristas</option></select><select aria-label="Filtrar por estado de cuenta" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setCuenta(event.target.value as EstadoCuenta | "")} value={cuenta}><option value="">Todos los accesos</option><option value="sin_cuenta">Sin cuenta web</option><option value="minorista">Cuenta minorista</option><option value="mayorista_pendiente">Mayorista pendiente</option><option value="mayorista_aprobado">Mayorista aprobado</option><option value="operador">Operador</option><option value="admin">Administrador</option></select><select aria-label="Ordenar clientes" className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-2.5" onChange={(event) => setOrden(event.target.value as FiltrosClientes["ordering"])} value={orden}><option value="nombre">Nombre</option><option value="-creado_en">Registro reciente</option><option value="-ultimo_pedido_en">Compra reciente</option><option value="-pedidos_total">Más pedidos</option><option value="-total_comprado">Mayor facturación</option></select><button className="rounded-xl bg-[#3B3B3B] px-5 py-2.5 font-black text-white disabled:opacity-50 md:col-span-2" disabled={cargando} type="submit">{cargando ? "Consultando..." : "Aplicar filtros"}</button></form>
          <div className="mt-5 grid gap-3">{clientes.length === 0 ? <p className="rounded-2xl border border-dashed border-[#3B3B3B]/20 p-6 text-center text-[#3B3B3B]/60">No hay clientes para los filtros seleccionados.</p> : clientes.map((cliente) => <button className={`w-full rounded-2xl border p-4 text-left ${seleccionado?.id === cliente.id ? "border-[#C41D85] bg-[#C41D85]/5" : "border-[#3B3B3B]/10"}`} key={cliente.id} onClick={() => setSeleccionado(cliente)} type="button"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex flex-wrap gap-2"><span className="rounded-full bg-[#FFEEDC] px-2.5 py-1 text-xs font-black capitalize">{cliente.tipo_cliente}</span><span className={`rounded-full px-2.5 py-1 text-xs font-black ${cliente.rol === "cliente_mayorista" && !cliente.mayorista_aprobado ? "bg-amber-50 text-amber-900" : "bg-green-50 text-green-800"}`}>{etiquetaCuenta(cliente)}</span></div><h3 className="mt-3 text-lg font-black">{cliente.razon_social || `${cliente.nombre} ${cliente.apellido}`.trim()}</h3><p className="mt-1 text-xs text-[#3B3B3B]/50">{cliente.email || cliente.whatsapp || "Sin contacto registrado"}</p></div><div className="text-right"><p className="text-lg font-black text-[#1D883F]">{importe(cliente.total_comprado)}</p><p className="mt-1 text-xs font-bold text-[#3B3B3B]/50">{cliente.pedidos_total} {cliente.pedidos_total === 1 ? "pedido" : "pedidos"}</p><p className="mt-2 text-xs text-[#3B3B3B]/50">{fecha(cliente.ultimo_pedido_en)}</p></div></div></button>)}</div>
          <div className="mt-5 flex justify-between gap-4"><button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 text-sm font-black disabled:opacity-40" disabled={pagina <= 1 || cargando} onClick={() => void aplicarFiltros(pagina - 1)} type="button">Anterior</button><button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 text-sm font-black disabled:opacity-40" disabled={pagina >= paginas || cargando} onClick={() => void aplicarFiltros(pagina + 1)} type="button">Siguiente</button></div>
        </section>
        <aside className="self-start rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5">{!seleccionado ? <div className="py-12 text-center"><p className="text-4xl">👤</p><h2 className="mt-4 text-xl font-black">Selecciona un cliente</h2><p className="mt-2 text-sm text-[#3B3B3B]/60">Aquí verás contacto, actividad y permisos comerciales.</p></div> : <><p className="text-xs font-black uppercase tracking-wider text-[#1D883F]">Ficha comercial</p><h2 className="mt-1 text-2xl font-black">{seleccionado.razon_social || `${seleccionado.nombre} ${seleccionado.apellido}`.trim()}</h2><dl className="mt-5 grid gap-3 text-sm"><div className="rounded-2xl bg-[#F8F1E8] p-4"><dt className="text-xs font-black uppercase text-[#3B3B3B]/45">Contacto</dt><dd className="mt-2 font-bold">{seleccionado.email || "Sin email"}</dd><dd className="mt-1">{seleccionado.whatsapp || seleccionado.telefono || "Sin teléfono"}</dd></div><div className="rounded-2xl bg-[#F8F1E8] p-4"><dt className="text-xs font-black uppercase text-[#3B3B3B]/45">Ubicación</dt><dd className="mt-2">{[seleccionado.direccion, seleccionado.ciudad, seleccionado.provincia].filter(Boolean).join(", ") || "Sin dirección"}</dd></div>{seleccionado.cuit && <div className="rounded-2xl bg-[#F8F1E8] p-4"><dt className="text-xs font-black uppercase text-[#3B3B3B]/45">Identificación fiscal</dt><dd className="mt-2 font-bold">{seleccionado.cuit}</dd></div>}</dl><a className="mt-5 inline-flex rounded-xl bg-[#FFEEDC] px-4 py-2.5 text-sm font-black" href={`/panel/pedidos?search=${encodeURIComponent(seleccionado.email || seleccionado.nombre)}`}>Ver historial de pedidos</a>
          {usuario.rol === "admin" && seleccionado.perfil_id && seleccionado.rol !== "admin" && <section className="mt-6 border-t border-[#3B3B3B]/10 pt-5" aria-label="Permisos del cliente"><p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Permisos administrativos</p><label className="mt-3 grid gap-1.5 text-sm font-bold">Rol de la cuenta<select className="rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-3" disabled={procesando} onChange={(event) => { const rol = event.target.value as "cliente_minorista" | "cliente_mayorista" | "operador"; void cambiarPerfil({ rol, mayorista_aprobado: rol === "cliente_mayorista" ? seleccionado.mayorista_aprobado : false }); }} value={seleccionado.rol ?? "cliente_minorista"}><option value="cliente_minorista">Cliente minorista</option><option value="cliente_mayorista">Cliente mayorista</option><option value="operador">Operador</option></select></label>{seleccionado.rol === "cliente_mayorista" && <button className={`mt-3 w-full rounded-xl px-4 py-3 font-black text-white disabled:opacity-50 ${seleccionado.mayorista_aprobado ? "bg-[#FF6515]" : "bg-[#1D883F]"}`} disabled={procesando} onClick={() => void cambiarPerfil({ mayorista_aprobado: !seleccionado.mayorista_aprobado })} type="button">{procesando ? "Actualizando..." : seleccionado.mayorista_aprobado ? "Suspender aprobación mayorista" : "Aprobar cuenta mayorista"}</button>}<p className="mt-3 text-xs text-[#3B3B3B]/50">Solo administradores pueden cambiar roles o aprobaciones. Los cambios se validan nuevamente en el servidor.</p></section>}
          {usuario.rol === "operador" && <p className="mt-6 rounded-2xl bg-[#F8F1E8] p-4 text-xs text-[#3B3B3B]/60">Vista de consulta. Las aprobaciones mayoristas requieren un administrador.</p>}</>}</aside>
      </div>
    </div>
  </main>;
}
