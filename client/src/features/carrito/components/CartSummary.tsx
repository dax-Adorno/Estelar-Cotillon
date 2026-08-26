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
    <section className="rounded-2xl bg-white p-4 ring-1 ring-[#FFBA1F]/40">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-black uppercase tracking-wide text-[#C41D85]">
            Carrito
          </p>
          <h2 className="mt-1 text-xl font-black text-[#3B3B3B]">
            Pedido actual
          </h2>
        </div>

        <div className="rounded-2xl bg-[#FFEEDC] px-4 py-3 text-center">
          <p className="text-xs font-black uppercase text-[#3B3B3B]/60">
            Unidades
          </p>
          <p className="text-2xl font-black text-[#FF6515]">{cantidadTotal}</p>
        </div>
      </div>

      {items.length === 0 ? (
        <p className="mt-5 rounded-2xl bg-[#FFEEDC] p-4 text-sm font-semibold text-[#3B3B3B]/70">
          Todavía no agregaste productos. Usá el catálogo para armar el pedido.
        </p>
      ) : (
        <div className="mt-5 grid gap-3">
          {items.map((item) => {
            const precioUnitario = Number(item.producto.precio_minorista);
            const subtotalItem = Number.isNaN(precioUnitario)
              ? 0
              : precioUnitario * item.cantidad;

            return (
              <article
                className="rounded-2xl border border-[#FFBA1F]/40 bg-white p-4"
                key={item.producto.id}
              >
                <div>
                  <p className="font-black leading-tight text-[#3B3B3B]">
                    {item.producto.nombre}
                  </p>
                  <p className="mt-1 text-xs font-bold text-[#3B3B3B]/55">
                    SKU: {item.producto.sku}
                  </p>
                </div>

                <div className="mt-4 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <button
                      aria-label={`Disminuir ${item.producto.nombre}`}
                      className="h-9 w-9 rounded-xl border border-[#FFBA1F]/60 bg-[#FFEEDC] font-black text-[#3B3B3B] transition hover:bg-[#FFBA1F]/30"
                      onClick={() => onDisminuirProducto(item.producto.id)}
                      type="button"
                    >
                      -
                    </button>

                    <span className="min-w-8 text-center font-black text-[#3B3B3B]">
                      {item.cantidad}
                    </span>

                    <button
                      aria-label={`Incrementar ${item.producto.nombre}`}
                      className="h-9 w-9 rounded-xl border border-[#FFBA1F]/60 bg-[#FFEEDC] font-black text-[#3B3B3B] transition hover:bg-[#FFBA1F]/30"
                      onClick={() => onIncrementarProducto(item.producto.id)}
                      type="button"
                    >
                      +
                    </button>
                  </div>

                  <button
                    className="text-sm font-black text-red-700 transition hover:text-red-800"
                    onClick={() => onQuitarProducto(item.producto.id)}
                    type="button"
                  >
                    Quitar
                  </button>
                </div>

                <div className="mt-4 rounded-xl bg-[#FFEEDC] p-3">
                  <p className="text-xs font-bold text-[#3B3B3B]/60">
                    Unitario: {formatearPrecio(precioUnitario)}
                  </p>
                  <p className="mt-1 font-black text-[#1D883F]">
                    Subtotal: {formatearPrecio(subtotalItem)}
                  </p>
                </div>
              </article>
            );
          })}

          <div className="rounded-2xl bg-[#3B3B3B] p-4 text-white">
            <p className="text-xs font-black uppercase text-white/60">
              Total estimado
            </p>
            <p className="mt-1 text-2xl font-black">
              {formatearPrecio(subtotal)}
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
