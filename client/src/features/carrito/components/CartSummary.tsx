import type { CarritoItem } from "../types";

interface CartSummaryProps {
  items: CarritoItem[];
  onIncrementarProducto: (productoId: number) => void;
  onDisminuirProducto: (productoId: number) => void;
  onQuitarProducto: (productoId: number) => void;
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

export function CartSummary({
  items,
  onIncrementarProducto,
  onDisminuirProducto,
  onQuitarProducto,
}: CartSummaryProps) {
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
          {items.map((item) => {
            const precioUnitario = Number(item.producto.precio_minorista);
            const subtotalItem = Number.isNaN(precioUnitario)
              ? 0
              : precioUnitario * item.cantidad;

            return (
              <article
                className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-orange-100 p-4"
                key={item.producto.id}
              >
                <div>
                  <p className="font-semibold text-slate-950">
                    {item.producto.nombre}
                  </p>
                  <p className="text-sm text-slate-500">
                    SKU: {item.producto.sku}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    Unitario: {formatearPrecio(precioUnitario)}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    aria-label={`Disminuir ${item.producto.nombre}`}
                    className="h-9 w-9 rounded-lg border border-orange-200 font-bold text-slate-700 transition hover:bg-orange-50"
                    onClick={() => onDisminuirProducto(item.producto.id)}
                    type="button"
                  >
                    -
                  </button>

                  <span className="min-w-8 text-center font-bold">
                    {item.cantidad}
                  </span>

                  <button
                    aria-label={`Incrementar ${item.producto.nombre}`}
                    className="h-9 w-9 rounded-lg border border-orange-200 font-bold text-slate-700 transition hover:bg-orange-50"
                    onClick={() => onIncrementarProducto(item.producto.id)}
                    type="button"
                  >
                    +
                  </button>
                </div>

                <div className="text-right">
                  <p className="font-semibold">
                    Subtotal: {formatearPrecio(subtotalItem)}
                  </p>

                  <button
                    className="mt-2 text-sm font-semibold text-red-700 transition hover:text-red-800"
                    onClick={() => onQuitarProducto(item.producto.id)}
                    type="button"
                  >
                    Quitar
                  </button>
                </div>
              </article>
            );
          })}

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
