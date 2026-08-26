import { useState } from "react";

import type { CarritoItem } from "../../carrito/types";
import type { DatosPedidoCliente, PedidoPublicoResponse } from "../types";

interface CheckoutPedidoProps {
  items: CarritoItem[];
  pedidoCreado: PedidoPublicoResponse | null;
  errorPedido: string | null;
  enviandoPedido: boolean;
  onEnviarPedido: (datos: DatosPedidoCliente) => Promise<void>;
}

function formatearPrecio(valor: number): string {
  return valor.toLocaleString("es-AR", {
    style: "currency",
    currency: "ARS",
  });
}

function calcularSubtotal(items: CarritoItem[]): number {
  return items.reduce((total, item) => {
    const precio = Number(item.producto.precio_minorista);

    if (Number.isNaN(precio)) {
      return total;
    }

    return total + precio * item.cantidad;
  }, 0);
}

export function CheckoutPedido({
  items,
  pedidoCreado,
  errorPedido,
  enviandoPedido,
  onEnviarPedido,
}: CheckoutPedidoProps) {
  const [nombreCompleto, setNombreCompleto] = useState("");
  const [email, setEmail] = useState("");
  const [whatsapp, setWhatsapp] = useState("");
  const [notas, setNotas] = useState("");

  const subtotal = calcularSubtotal(items);
  const carritoVacio = items.length === 0;

  return (
    <section className="mt-5 rounded-2xl bg-white p-4 ring-1 ring-[#FFBA1F]/40">
      <div>
        <p className="text-sm font-black uppercase tracking-wide text-[#C41D85]">
          Checkout
        </p>
        <h2 className="mt-1 text-xl font-black text-[#3B3B3B]">
          Datos del cliente
        </h2>
        <p className="mt-2 text-sm text-[#3B3B3B]/70">
          El pedido se registra en el sistema para seguimiento operativo.
        </p>
      </div>

      {carritoVacio && !pedidoCreado ? (
        <p className="mt-5 rounded-2xl bg-[#FFEEDC] p-4 text-sm font-semibold text-[#3B3B3B]/70">
          Agregá productos antes de completar los datos del cliente.
        </p>
      ) : null}

      {!carritoVacio && (
        <form
          className="mt-5 grid gap-4"
          onSubmit={(event) => {
            event.preventDefault();

            void onEnviarPedido({
              nombreCompleto,
              email,
              whatsapp,
              notas,
            });
          }}
        >
          <div>
            <label
              className="text-sm font-black text-[#3B3B3B]"
              htmlFor="nombre-completo"
            >
              Nombre completo
            </label>
            <input
              className="mt-2 w-full rounded-2xl border border-[#FFBA1F]/60 px-4 py-3 text-sm outline-none focus:border-[#FF6515] focus:ring-4 focus:ring-[#FFBA1F]/30"
              id="nombre-completo"
              onChange={(event) => setNombreCompleto(event.target.value)}
              required
              type="text"
              value={nombreCompleto}
            />
          </div>

          <div>
            <label
              className="text-sm font-black text-[#3B3B3B]"
              htmlFor="email"
            >
              Email
            </label>
            <input
              className="mt-2 w-full rounded-2xl border border-[#FFBA1F]/60 px-4 py-3 text-sm outline-none focus:border-[#FF6515] focus:ring-4 focus:ring-[#FFBA1F]/30"
              id="email"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </div>

          <div>
            <label
              className="text-sm font-black text-[#3B3B3B]"
              htmlFor="whatsapp"
            >
              WhatsApp
            </label>
            <input
              className="mt-2 w-full rounded-2xl border border-[#FFBA1F]/60 px-4 py-3 text-sm outline-none focus:border-[#FF6515] focus:ring-4 focus:ring-[#FFBA1F]/30"
              id="whatsapp"
              onChange={(event) => setWhatsapp(event.target.value)}
              required
              type="tel"
              value={whatsapp}
            />
          </div>

          <div>
            <label
              className="text-sm font-black text-[#3B3B3B]"
              htmlFor="notas"
            >
              Notas del pedido
            </label>
            <textarea
              className="mt-2 min-h-24 w-full rounded-2xl border border-[#FFBA1F]/60 px-4 py-3 text-sm outline-none focus:border-[#FF6515] focus:ring-4 focus:ring-[#FFBA1F]/30"
              id="notas"
              onChange={(event) => setNotas(event.target.value)}
              value={notas}
            />
          </div>

          <div className="rounded-2xl bg-[#FFEEDC] p-4">
            <p className="text-xs font-black uppercase text-[#3B3B3B]/60">
              Total a registrar
            </p>
            <p className="mt-1 text-2xl font-black text-[#FF6515]">
              {formatearPrecio(subtotal)}
            </p>

            <button
              className="mt-4 w-full rounded-2xl bg-[#1D883F] px-5 py-3 font-black text-white shadow-sm transition hover:bg-[#FF6515] disabled:cursor-not-allowed disabled:opacity-60"
              disabled={enviandoPedido}
              type="submit"
            >
              {enviandoPedido ? "Enviando pedido..." : "Crear pedido"}
            </button>
          </div>
        </form>
      )}

      {errorPedido && (
        <div className="mt-5 rounded-2xl bg-red-50 p-4 text-red-700">
          <p className="font-black">No se pudo crear el pedido.</p>
          <p className="mt-1 text-sm">{errorPedido}</p>
        </div>
      )}

      {pedidoCreado && (
        <div className="mt-5 rounded-2xl bg-[#1D883F]/10 p-4 text-[#1D883F]">
          <p className="font-black">Pedido creado correctamente.</p>
          <p className="mt-1 text-sm">Código: {pedidoCreado.codigo}</p>
          <p className="text-sm">Cliente: {pedidoCreado.cliente_nombre}</p>
          <p className="text-sm">
            Total: {formatearPrecio(Number(pedidoCreado.total))}
          </p>
        </div>
      )}
    </section>
  );
}
