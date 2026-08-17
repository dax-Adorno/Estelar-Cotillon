import type { CarritoItem } from "../types";

interface CartSummaryProps {
  items: CarritoItem[];
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

function calcularCantidadTotal(items: CarritoItem[]): number {
  return items.reduce((total, item) => total + item.cantidad, 0);
}

export function CartSummary({ items }: CartSummaryProps) {
  const cantidadTotal = calcularCantidadTotal(items);
  const subtotal = calcularSubtotal(items);

  return (
    <section className="mt-10 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-orange-100">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-950">Carrito</h2>
          <p className="mt-2 text-slate-600">
            Resumen inicial de productos seleccionados.
          </p>
        </div>

        <div className="rounded-xl bg-orange-50 px-5 py-4 text-right">
          <p className="text-sm font-semibold text-slate-500">
            Productos seleccionados
          </p>
          <p className="text-3xl font-bold text-slate-950">{cantidadTotal}</p>
        </div>
      </div>

      {items.length === 0 ? (
        <p className="mt-6 rounded-xl bg-orange-50 p-4 text-slate-600">
          Todavía no agregaste productos al carrito.
        </p>
      ) : (
        <div className="mt-6 grid gap-3">
          {items.map((item) => (
            <article
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-orange-100 p-4"
              key={item.producto.id}
            >
              <div>
                <p className="font-semibold text-slate-950">
                  {item.producto.nombre}
                </p>
                <p className="text-sm text-slate-500">
                  SKU: {item.producto.sku}
                </p>
              </div>

              <div className="text-right">
                <p className="font-semibold">Cantidad: {item.cantidad}</p>
                <p className="text-sm text-slate-500">
                  Unitario: {formatearPrecio(Number(item.producto.precio_minorista))}
                </p>
              </div>
            </article>
          ))}

          <div className="mt-4 flex justify-end">
            <p className="rounded-xl bg-orange-50 px-5 py-4 text-xl font-bold text-slate-950">
              Subtotal: {formatearPrecio(subtotal)}
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
