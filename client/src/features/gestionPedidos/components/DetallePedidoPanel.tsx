import { useState } from "react";

import { ETIQUETAS_ESTADO, ETIQUETAS_PAGO } from "../etiquetas";
import { cambiarEstadoPago, cambiarEstadoPedido } from "../gestionPedidosApi";
import type { EstadoPago, EstadoPedido, PedidoDetalle, PedidoResumen } from "../types";

const TRANSICIONES_ESTADO: Record<EstadoPedido, EstadoPedido[]> = {
  borrador: ["pendiente", "cancelado"],
  pendiente: ["confirmado", "cancelado"],
  confirmado: ["entregado", "cancelado"],
  entregado: [],
  cancelado: [],
};

const TRANSICIONES_PAGO: Record<EstadoPago, EstadoPago[]> = {
  pendiente: ["parcial", "pagado"],
  parcial: ["pagado", "reembolsado"],
  pagado: ["reembolsado"],
  reembolsado: [],
};

function importe(valor: string): string {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(Number(valor));
}

function fecha(valor: string): string {
  return new Intl.DateTimeFormat("es-AR", { dateStyle: "short", timeStyle: "short" }).format(new Date(valor));
}

interface DetallePedidoPanelProps {
  detalle: PedidoDetalle;
  resumen: PedidoResumen;
  onActualizar: (pedido: PedidoDetalle) => Promise<void>;
  onCerrar: () => void;
}

export function DetallePedidoPanel({ detalle, resumen, onActualizar, onCerrar }: DetallePedidoPanelProps) {
  const [estadoDestino, setEstadoDestino] = useState<EstadoPedido | "">("");
  const [pagoDestino, setPagoDestino] = useState<EstadoPago | "">("");
  const [comentarioEstado, setComentarioEstado] = useState("");
  const [comentarioPago, setComentarioPago] = useState("");
  const [procesando, setProcesando] = useState<"estado" | "pago" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pedidoCobrado = ["parcial", "pagado"].includes(detalle.estado_pago);
  const destinosEstado = TRANSICIONES_ESTADO[detalle.estado].filter(
    (destino) => destino !== "cancelado" || !pedidoCobrado,
  );
  const destinosPago = TRANSICIONES_PAGO[detalle.estado_pago];

  async function ejecutar(tipo: "estado" | "pago") {
    setProcesando(tipo);
    setError(null);
    try {
      const actualizado = tipo === "estado"
        ? await cambiarEstadoPedido(detalle.id, estadoDestino as EstadoPedido, comentarioEstado.trim())
        : await cambiarEstadoPago(detalle.id, pagoDestino as EstadoPago, comentarioPago.trim());
      if (tipo === "estado") setComentarioEstado("");
      else setComentarioPago("");
      await onActualizar(actualizado);
    } catch (unknownError) {
      setError(unknownError instanceof Error ? unknownError.message : "No se pudo actualizar el pedido.");
    } finally {
      setProcesando(null);
    }
  }

  return (
    <section aria-label={`Detalle del pedido ${detalle.codigo}`} className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">Detalle operativo</p>
          <h2 className="mt-1 text-2xl font-black">{detalle.codigo}</h2>
          <p className="mt-2 text-sm text-[#3B3B3B]/60">{detalle.cliente_nombre} · {resumen.cliente_email}</p>
        </div>
        <button className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 text-sm font-black" onClick={onCerrar} type="button">Cerrar detalle</button>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl bg-[#F8F1E8] p-4"><p className="text-xs font-black uppercase text-[#3B3B3B]/45">Estado</p><p className="mt-2 font-black">{ETIQUETAS_ESTADO[detalle.estado]}</p></div>
        <div className="rounded-2xl bg-[#F8F1E8] p-4"><p className="text-xs font-black uppercase text-[#3B3B3B]/45">Pago</p><p className="mt-2 font-black">{ETIQUETAS_PAGO[detalle.estado_pago]}</p></div>
        <div className="rounded-2xl bg-[#F8F1E8] p-4"><p className="text-xs font-black uppercase text-[#3B3B3B]/45">Total</p><p className="mt-2 font-black text-[#1D883F]">{importe(detalle.total)}</p></div>
        <div className="rounded-2xl bg-[#F8F1E8] p-4"><p className="text-xs font-black uppercase text-[#3B3B3B]/45">Creado</p><p className="mt-2 text-sm font-black">{fecha(detalle.creado_en)}</p></div>
      </div>

      {error && <p className="mt-5 rounded-xl bg-red-50 p-3 text-sm font-bold text-red-700" role="alert">{error}</p>}
      {pedidoCobrado && TRANSICIONES_ESTADO[detalle.estado].includes("cancelado") && (
        <p className="mt-5 rounded-xl bg-amber-50 p-3 text-sm font-bold text-amber-900">Para cancelar este pedido primero registra el reembolso.</p>
      )}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <form className="rounded-2xl border border-[#3B3B3B]/10 p-4" onSubmit={(event) => { event.preventDefault(); void ejecutar("estado"); }}>
          <h3 className="font-black">Avanzar estado operativo</h3>
          {destinosEstado.length === 0 ? <p className="mt-3 text-sm text-[#3B3B3B]/60">No hay transiciones operativas disponibles.</p> : <><select aria-label="Nuevo estado del pedido" className="mt-3 w-full rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-3" onChange={(event) => setEstadoDestino(event.target.value as EstadoPedido)} required value={estadoDestino}><option value="">Seleccionar acción</option>{destinosEstado.map((estado) => <option key={estado} value={estado}>{ETIQUETAS_ESTADO[estado]}</option>)}</select><textarea aria-label="Comentario del estado" className="mt-3 min-h-20 w-full rounded-xl border border-[#3B3B3B]/15 px-4 py-3" maxLength={500} onChange={(event) => setComentarioEstado(event.target.value)} placeholder="Comentario para auditoría (opcional)" value={comentarioEstado} /><button className="mt-3 rounded-xl bg-[#1D883F] px-4 py-2.5 font-black text-white disabled:opacity-50" disabled={!estadoDestino || procesando !== null} type="submit">{procesando === "estado" ? "Actualizando..." : "Aplicar estado"}</button></>}
        </form>
        <form className="rounded-2xl border border-[#3B3B3B]/10 p-4" onSubmit={(event) => { event.preventDefault(); void ejecutar("pago"); }}>
          <h3 className="font-black">Actualizar estado de pago</h3>
          {destinosPago.length === 0 ? <p className="mt-3 text-sm text-[#3B3B3B]/60">No hay transiciones de pago disponibles.</p> : <><select aria-label="Nuevo estado del pago" className="mt-3 w-full rounded-xl border border-[#3B3B3B]/15 bg-white px-4 py-3" onChange={(event) => setPagoDestino(event.target.value as EstadoPago)} required value={pagoDestino}><option value="">Seleccionar acción</option>{destinosPago.map((estado) => <option key={estado} value={estado}>{ETIQUETAS_PAGO[estado]}</option>)}</select><textarea aria-label="Comentario del pago" className="mt-3 min-h-20 w-full rounded-xl border border-[#3B3B3B]/15 px-4 py-3" maxLength={500} onChange={(event) => setComentarioPago(event.target.value)} placeholder="Referencia o comentario (opcional)" value={comentarioPago} /><button className="mt-3 rounded-xl bg-[#C41D85] px-4 py-2.5 font-black text-white disabled:opacity-50" disabled={!pagoDestino || procesando !== null} type="submit">{procesando === "pago" ? "Actualizando..." : "Aplicar pago"}</button></>}
        </form>
      </div>

      <div className="mt-6 overflow-hidden rounded-2xl border border-[#3B3B3B]/10">
        <table className="w-full min-w-[580px] text-left text-sm"><thead className="bg-[#FFEEDC] text-xs uppercase text-[#3B3B3B]/60"><tr><th className="px-4 py-3">Producto</th><th className="px-4 py-3 text-right">Cantidad</th><th className="px-4 py-3 text-right">Unitario</th><th className="px-4 py-3 text-right">Subtotal</th></tr></thead><tbody>{detalle.detalles.map((linea) => <tr className="border-t border-[#3B3B3B]/8" key={linea.id}><td className="px-4 py-3"><span className="font-black">{linea.producto_nombre}</span><span className="mt-1 block text-xs text-[#3B3B3B]/50">{linea.producto_sku}</span></td><td className="px-4 py-3 text-right font-bold">{linea.cantidad}</td><td className="px-4 py-3 text-right">{importe(linea.precio_unitario)}</td><td className="px-4 py-3 text-right font-black">{importe(linea.subtotal)}</td></tr>)}</tbody><tfoot className="bg-[#F8F1E8] font-black"><tr><td className="px-4 py-3 text-right" colSpan={3}>Subtotal</td><td className="px-4 py-3 text-right">{importe(detalle.subtotal)}</td></tr>{Number(detalle.descuento) > 0 && <tr><td className="px-4 py-3 text-right" colSpan={3}>Descuento</td><td className="px-4 py-3 text-right text-[#C41D85]">− {importe(detalle.descuento)}</td></tr>}<tr><td className="px-4 py-3 text-right" colSpan={3}>Total</td><td className="px-4 py-3 text-right text-[#1D883F]">{importe(detalle.total)}</td></tr></tfoot></table>
      </div>

      {(detalle.notas || detalle.promocion_nombre) && <div className="mt-5 grid gap-3 sm:grid-cols-2">{detalle.notas && <div className="rounded-2xl bg-[#F8F1E8] p-4"><p className="text-xs font-black uppercase text-[#3B3B3B]/45">Notas del cliente</p><p className="mt-2 text-sm">{detalle.notas}</p></div>}{detalle.promocion_nombre && <div className="rounded-2xl bg-[#F8F1E8] p-4"><p className="text-xs font-black uppercase text-[#3B3B3B]/45">Promoción aplicada</p><p className="mt-2 text-sm font-black">{detalle.promocion_nombre}</p></div>}</div>}

      <section className="mt-6" aria-label="Historial del pedido"><h3 className="text-xl font-black">Historial auditable</h3>{detalle.eventos.length === 0 ? <p className="mt-3 rounded-2xl border border-dashed border-[#3B3B3B]/20 p-4 text-sm text-[#3B3B3B]/60">Todavía no hay cambios registrados.</p> : <ol className="mt-4 grid gap-3">{detalle.eventos.map((evento) => <li className="rounded-2xl bg-[#F8F1E8] p-4" key={evento.id}><div className="flex flex-wrap justify-between gap-2"><p className="text-sm font-black">{evento.tipo === "estado" ? "Estado operativo" : "Estado de pago"}: {evento.valor_anterior} → {evento.valor_nuevo}</p><time className="text-xs font-bold text-[#3B3B3B]/50">{fecha(evento.creado_en)}</time></div>{evento.comentario && <p className="mt-2 text-sm">{evento.comentario}</p>}<p className="mt-2 text-xs text-[#3B3B3B]/50">{evento.usuario_email || "Sistema"}</p></li>)}</ol>}</section>
    </section>
  );
}
