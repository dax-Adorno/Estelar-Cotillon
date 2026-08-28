import { useEffect, useMemo, useState } from "react";

import { cerrarSesion, obtenerSesionActual } from "../../auth/authApi";
import type { UsuarioActual } from "../../auth/types";
import { obtenerResumenComercial } from "../reportesApi";
import type { ResumenComercial } from "../types";

const ETIQUETAS_ESTADO: Record<string, string> = {
  pendiente: "Pendientes",
  confirmado: "Confirmados",
  en_preparacion: "En preparación",
  listo: "Listos",
  entregado: "Entregados",
  cancelado: "Cancelados",
};

const ETIQUETAS_CANAL: Record<string, string> = {
  web: "Tienda web",
  whatsapp: "WhatsApp",
  instagram: "Instagram",
  mercadolibre: "Mercado Libre",
  tiendanube: "Tienda Nube",
  mostrador: "Mostrador",
  otro: "Otro",
};

function formatearImporte(valor: string): string {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  }).format(Number(valor));
}

function formatearFecha(valor: string): string {
  return new Intl.DateTimeFormat("es-AR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(valor));
}

interface TarjetaKpiProps {
  acento: string;
  etiqueta: string;
  nota: string;
  valor: string | number;
}

function TarjetaKpi({ acento, etiqueta, nota, valor }: TarjetaKpiProps) {
  return (
    <article className="rounded-3xl bg-white p-5 shadow-sm ring-1 ring-black/5">
      <div className={`h-1.5 w-12 rounded-full ${acento}`} />
      <p className="mt-4 text-xs font-black uppercase tracking-wider text-[#3B3B3B]/55">
        {etiqueta}
      </p>
      <p className="mt-2 text-3xl font-black text-[#3B3B3B]">{valor}</p>
      <p className="mt-2 text-xs font-semibold text-[#3B3B3B]/60">{nota}</p>
    </article>
  );
}

interface DistribucionProps {
  color: string;
  items: Array<{ cantidad: number; etiqueta: string }>;
  titulo: string;
}

function Distribucion({ color, items, titulo }: DistribucionProps) {
  const maximo = Math.max(...items.map((item) => item.cantidad), 1);

  return (
    <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5">
      <h2 className="text-xl font-black text-[#3B3B3B]">{titulo}</h2>
      {items.length === 0 ? (
        <p className="mt-6 rounded-2xl bg-[#FFEEDC] p-4 text-sm text-[#3B3B3B]/65">
          Todavía no hay pedidos para mostrar.
        </p>
      ) : (
        <div className="mt-6 grid gap-4">
          {items.map((item) => (
            <div key={item.etiqueta}>
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-bold text-[#3B3B3B]/75">
                  {item.etiqueta}
                </span>
                <span className="font-black text-[#3B3B3B]">
                  {item.cantidad}
                </span>
              </div>
              <div className="mt-2 h-2.5 overflow-hidden rounded-full bg-[#3B3B3B]/8">
                <div
                  aria-hidden="true"
                  className={`h-full rounded-full ${color}`}
                  style={{ width: `${(item.cantidad / maximo) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function PantallaMensaje({
  children,
  titulo,
}: {
  children: React.ReactNode;
  titulo: string;
}) {
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

export function PanelOperativo() {
  const [usuario, setUsuario] = useState<UsuarioActual | null>(null);
  const [resumen, setResumen] = useState<ResumenComercial | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    let activo = true;

    async function cargarPanel(): Promise<void> {
      setCargando(true);
      setError(null);
      try {
        const sesion = await obtenerSesionActual();
        if (!activo) return;
        setUsuario(sesion);

        if (!sesion || !["operador", "admin"].includes(sesion.rol)) {
          return;
        }

        const datos = await obtenerResumenComercial();
        if (activo) setResumen(datos);
      } catch (unknownError) {
        if (activo) {
          setError(
            unknownError instanceof Error
              ? unknownError.message
              : "No se pudo cargar el panel operativo.",
          );
        }
      } finally {
        if (activo) setCargando(false);
      }
    }

    void cargarPanel();
    return () => {
      activo = false;
    };
  }, [revision]);

  const estados = useMemo(
    () =>
      resumen?.pedidos_por_estado.map((item) => ({
        cantidad: item.cantidad,
        etiqueta: ETIQUETAS_ESTADO[item.estado] ?? item.estado,
      })) ?? [],
    [resumen],
  );

  const canales = useMemo(
    () =>
      resumen?.pedidos_por_canal.map((item) => ({
        cantidad: item.cantidad,
        etiqueta: ETIQUETAS_CANAL[item.canal_venta] ?? item.canal_venta,
      })) ?? [],
    [resumen],
  );

  async function salir(): Promise<void> {
    await cerrarSesion();
    window.location.assign("/#acceso");
  }

  if (cargando) {
    return (
      <PantallaMensaje titulo="Preparando panel operativo">
        <p role="status">Consultando identidad, permisos y métricas actuales...</p>
      </PantallaMensaje>
    );
  }

  if (!usuario) {
    return (
      <PantallaMensaje titulo="Inicia sesión para continuar">
        <p>El panel está reservado para operadores y administradores.</p>
        <a
          className="mt-6 inline-flex rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white"
          href="/#acceso"
        >
          Ir al acceso
        </a>
      </PantallaMensaje>
    );
  }

  if (!["operador", "admin"].includes(usuario.rol)) {
    return (
      <PantallaMensaje titulo="Acceso operativo restringido">
        <p>Tu cuenta está activa, pero no posee permisos internos.</p>
        <a
          className="mt-6 inline-flex rounded-xl border border-[#3B3B3B]/20 px-5 py-3 font-black"
          href="/"
        >
          Volver al catálogo
        </a>
      </PantallaMensaje>
    );
  }

  if (error || !resumen) {
    return (
      <PantallaMensaje titulo="No pudimos cargar las métricas">
        <p role="alert">{error ?? "La respuesta del servidor está incompleta."}</p>
        <button
          className="mt-6 rounded-xl bg-[#C41D85] px-5 py-3 font-black text-white"
          onClick={() => setRevision((actual) => actual + 1)}
          type="button"
        >
          Reintentar
        </button>
      </PantallaMensaje>
    );
  }

  const metricas = resumen.metricas;

  return (
    <main className="min-h-screen bg-[#F8F1E8] text-[#3B3B3B]">
      <header className="border-b border-[#3B3B3B]/10 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <div className="flex items-center gap-4">
            <img alt="ESTELART" className="h-11 w-auto" src="/brand/estelart-logo.svg" />
            <div>
              <p className="text-xs font-black uppercase tracking-wider text-[#C41D85]">
                Operaciones
              </p>
              <p className="font-black">Panel comercial</p>
            </div>
          </div>
          <nav className="flex flex-wrap items-center gap-2 text-sm font-black" aria-label="Navegación operativa">
            <a className="rounded-xl bg-[#FFEEDC] px-4 py-2" href="/panel">
              Resumen
            </a>
            <a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/panel/catalogo">
              Catálogo
            </a>
            <a className="rounded-xl px-4 py-2 hover:bg-[#FFEEDC]" href="/">
              Ver tienda
            </a>
            <button
              className="rounded-xl border border-[#3B3B3B]/15 px-4 py-2 hover:bg-[#FFEEDC]"
              onClick={() => void salir()}
              type="button"
            >
              Cerrar sesión
            </button>
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <section className="flex flex-wrap items-end justify-between gap-5">
          <div>
            <p className="text-sm font-black uppercase tracking-wider text-[#1D883F]">
              Estado general
            </p>
            <h1 className="mt-2 text-4xl font-black tracking-tight">
              Buen día, {usuario.nombre || "equipo"}
            </h1>
            <p className="mt-3 max-w-2xl text-[#3B3B3B]/65">
              Vista operativa para detectar pedidos pendientes, productos con
              poco stock y rendimiento comercial.
            </p>
          </div>
          <div className="rounded-2xl bg-white px-4 py-3 text-right shadow-sm ring-1 ring-black/5">
            <p className="text-xs font-black uppercase text-[#3B3B3B]/45">
              Datos actualizados
            </p>
            <p className="mt-1 text-sm font-bold">
              {formatearFecha(resumen.generado_en)}
            </p>
          </div>
        </section>

        <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Indicadores principales">
          <TarjetaKpi
            acento="bg-[#1D883F]"
            etiqueta="Total estimado"
            nota="Suma histórica de pedidos registrados"
            valor={formatearImporte(metricas.total_estimado)}
          />
          <TarjetaKpi
            acento="bg-[#FF6515]"
            etiqueta="Pedidos pendientes"
            nota="Requieren revisión del equipo"
            valor={metricas.pedidos_pendientes}
          />
          <TarjetaKpi
            acento="bg-[#C41D85]"
            etiqueta="Stock bajo"
            nota={`Productos con ${resumen.stock_bajo_umbral} unidades o menos`}
            valor={metricas.productos_stock_bajo}
          />
          <TarjetaKpi
            acento="bg-[#FFBA1F]"
            etiqueta="Promociones vigentes"
            nota="Activas en la fecha de consulta"
            valor={metricas.promociones_activas}
          />
        </section>

        <section className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-label="Indicadores de volumen">
          <TarjetaKpi acento="bg-[#3B3B3B]" etiqueta="Pedidos" nota="Pedidos históricos" valor={metricas.pedidos_total} />
          <TarjetaKpi acento="bg-[#3B3B3B]" etiqueta="Unidades" nota="Unidades pedidas" valor={metricas.unidades_pedidas} />
          <TarjetaKpi acento="bg-[#3B3B3B]" etiqueta="Productos" nota="Productos activos" valor={metricas.productos_activos} />
          <TarjetaKpi acento="bg-[#3B3B3B]" etiqueta="Categorías" nota="Categorías activas" valor={metricas.categorias_activas} />
        </section>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <Distribucion color="bg-[#FF6515]" items={estados} titulo="Pedidos por estado" />
          <Distribucion color="bg-[#C41D85]" items={canales} titulo="Pedidos por canal" />
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <section className="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-black/5">
            <div className="p-6">
              <p className="text-xs font-black uppercase tracking-wider text-[#1D883F]">Demanda</p>
              <h2 className="mt-1 text-2xl font-black">Productos más pedidos</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[560px] text-left text-sm">
                <thead className="bg-[#FFEEDC] text-xs uppercase text-[#3B3B3B]/60">
                  <tr>
                    <th className="px-6 py-3">Producto</th>
                    <th className="px-4 py-3 text-right">Unidades</th>
                    <th className="px-6 py-3 text-right">Importe</th>
                  </tr>
                </thead>
                <tbody>
                  {resumen.top_productos.length === 0 ? (
                    <tr><td className="px-6 py-6 text-[#3B3B3B]/60" colSpan={3}>Todavía no hay ventas para clasificar.</td></tr>
                  ) : (
                    resumen.top_productos.map((producto) => (
                      <tr className="border-t border-[#3B3B3B]/8" key={producto.producto_id}>
                        <td className="px-6 py-4"><span className="font-black">{producto.nombre}</span><span className="mt-1 block text-xs text-[#3B3B3B]/50">{producto.sku}</span></td>
                        <td className="px-4 py-4 text-right font-black">{producto.unidades}</td>
                        <td className="px-6 py-4 text-right font-black text-[#1D883F]">{formatearImporte(producto.importe)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-black/5">
            <p className="text-xs font-black uppercase tracking-wider text-[#FF6515]">Atención operativa</p>
            <h2 className="mt-1 text-2xl font-black">Reposición de stock</h2>
            {resumen.productos_stock_bajo.length === 0 ? (
              <p className="mt-6 rounded-2xl bg-green-50 p-4 text-sm font-bold text-green-800">No hay productos activos por debajo del umbral.</p>
            ) : (
              <ul className="mt-5 grid gap-3">
                {resumen.productos_stock_bajo.map((producto) => (
                  <li className="flex items-center justify-between gap-4 rounded-2xl bg-red-50 p-4" key={producto.id}>
                    <div><p className="font-black">{producto.nombre}</p><p className="mt-1 text-xs text-[#3B3B3B]/55">{producto.sku}</p></div>
                    <span className="rounded-full bg-white px-3 py-2 text-sm font-black text-red-700">{producto.stock} u.</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <footer className="mt-8 rounded-2xl border border-[#3B3B3B]/10 bg-white/70 p-4 text-xs text-[#3B3B3B]/55">
          Fuente: API interna de reportes ESTELART. El total estimado suma los
          pedidos registrados y no equivale necesariamente a ingresos cobrados.
        </footer>
      </div>
    </main>
  );
}
