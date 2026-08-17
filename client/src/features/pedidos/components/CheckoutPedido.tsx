import { useState } from "react";

import type { CarritoItem } from "../../carrito/types";
import type { DatosPedidoCliente, PedidoPreparado } from "../types";

interface CheckoutPedidoProps {
  items: CarritoItem[];
  pedidoPreparado: PedidoPreparado | null;
  onPrepararPedido: (datos: DatosPedidoCliente) => void;
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
  pedidoPreparado,
  onPrepararPedido,
}: CheckoutPedidoProps) {
  const [nombreCompleto, setNombreCompleto] = useState("");
  const [email, setEmail] = useState("");
  const [whatsapp, setWhatsapp] = useState("");
  const [notas, setNotas] = useState("");

  const subtotal = calcularSubtotal(items);
  const carritoVacio = items.length === 0;

  return (
    <section className="mt-10 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
      <div>
        <h2 className="text-2xl font-bold text-slate-950">
          Preparar pedido
        </h2>
        <p className="mt-2 text-slate-600">
          Completá los datos del cliente para preparar la solicitud comercial.
        </p>
      </div>

      {carritoVacio ? (
        <p className="mt-6 rounded-xl bg-orange-50 p-4 text-slate-600">
          Agregá productos al carrito antes de preparar un pedido.
        </p>
      ) : (
        <form
          className="mt-6 grid gap-4"
          onSubmit={(event) => {
            event.preventDefault();

            onPrepararPedido({
              nombreCompleto,
              email,
              whatsapp,
              notas,
            });
          }}
        >
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label
                className="text-sm font-semibold text-slate-700"
                htmlFor="nombre-completo"
              >
                Nombre completo
              </label>
              <input
                className="mt-2 w-full rounded-xl border border-orange-200 px-4 py-3 outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200"
                id="nombre-completo"
                onChange={(event) => setNombreCompleto(event.target.value)}
                required
                type="text"
                value={nombreCompleto}
              />
            </div>

            <div>
              <label
                className="text-sm font-semibold text-slate-700"
                htmlFor="email"
              >
                Email
              </label>
              <input
                className="mt-2 w-full rounded-xl border border-orange-200 px-4 py-3 outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200"
                id="email"
                onChange={(event) => setEmail(event.target.value)}
                required
                type="email"
                value={email}
              />
            </div>

            <div>
              <label
                className="text-sm font-semibold text-slate-700"
                htmlFor="whatsapp"
              >
                WhatsApp
              </label>
              <input
                className="mt-2 w-full rounded-xl border border-orange-200 px-4 py-3 outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200"
                id="whatsapp"
                onChange={(event) => setWhatsapp(event.target.value)}
                required
                type="tel"
                value={whatsapp}
              />
            </div>
          </div>

          <div>
            <label
              className="text-sm font-semibold text-slate-700"
              htmlFor="notas"
            >
              Notas del pedido
            </label>
            <textarea
              className="mt-2 min-h-28 w-full rounded-xl border border-orange-200 px-4 py-3 outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-200"
              id="notas"
              onChange={(event) => setNotas(event.target.value)}
              value={notas}
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl bg-orange-50 p-4">
            <p className="font-semibold text-slate-950">
              Total estimado: {formatearPrecio(subtotal)}
            </p>

            <button
              className="rounded-xl bg-orange-600 px-5 py-3 font-semibold text-white transition hover:bg-orange-700"
              type="submit"
            >
              Preparar pedido
            </button>
          </div>
        </form>
      )}

      {pedidoPreparado && (
        <div className="mt-6 rounded-xl bg-emerald-50 p-4 text-emerald-800">
          <p className="font-bold">Pedido preparado correctamente.</p>
          <p className="mt-1 text-sm">
            Cliente: {pedidoPreparado.cliente.nombreCompleto}
          </p>
          <p className="text-sm">
            Total: {formatearPrecio(pedidoPreparado.total)}
          </p>
        </div>
      )}
    </section>
  );
}
