import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { obtenerSesionActual } from "../../auth/authApi";
import type { UsuarioActual } from "../../auth/types";
import { obtenerResumenComercial } from "../reportesApi";
import type { ResumenComercial } from "../types";
import { PanelOperativo } from "./PanelOperativo";

vi.mock("../../auth/authApi", () => ({
  cerrarSesion: vi.fn(),
  obtenerSesionActual: vi.fn(),
}));

vi.mock("../reportesApi", () => ({
  obtenerResumenComercial: vi.fn(),
}));

const OPERADOR: UsuarioActual = {
  id: 12,
  email: "operador@estelart.test",
  nombre: "Omar",
  apellido: "Operador",
  rol: "operador",
  mayorista_aprobado: false,
};

const CLIENTE: UsuarioActual = {
  ...OPERADOR,
  id: 13,
  email: "cliente@estelart.test",
  rol: "cliente_minorista",
};

const RESUMEN: ResumenComercial = {
  generado_en: "2026-08-27T12:00:00-03:00",
  stock_bajo_umbral: 10,
  metricas: {
    pedidos_total: 18,
    pedidos_pendientes: 4,
    total_estimado: "125000.00",
    unidades_pedidas: 47,
    productos_activos: 32,
    productos_stock_bajo: 1,
    categorias_activas: 6,
    promociones_activas: 2,
  },
  pedidos_por_estado: [
    { estado: "pendiente", cantidad: 4 },
    { estado: "entregado", cantidad: 14 },
  ],
  pedidos_por_canal: [{ canal_venta: "web", cantidad: 18 }],
  top_productos: [
    {
      producto_id: 5,
      sku: "SLI-005",
      nombre: "Kit slime premium",
      unidades: 12,
      importe: "48000.00",
    },
  ],
  productos_stock_bajo: [
    { id: 8, sku: "GLO-008", nombre: "Globos pastel", stock: 5 },
  ],
};

describe("PanelOperativo", () => {
  beforeEach(() => {
    vi.mocked(obtenerSesionActual).mockReset();
    vi.mocked(obtenerResumenComercial).mockReset();
  });

  it("presenta un resumen accionable a operadores", async () => {
    vi.mocked(obtenerSesionActual).mockResolvedValue(OPERADOR);
    vi.mocked(obtenerResumenComercial).mockResolvedValue(RESUMEN);

    render(<PanelOperativo />);

    expect(
      await screen.findByRole("heading", { name: "Buen día, Omar" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Pedidos pendientes")).toBeInTheDocument();
    expect(screen.getByText("Kit slime premium")).toBeInTheDocument();
    expect(screen.getByText("Globos pastel")).toBeInTheDocument();
    expect(screen.getByText("Entregados")).toBeInTheDocument();
    expect(screen.getByText("Tienda web")).toBeInTheDocument();
    expect(screen.getByText("5 u.")).toBeInTheDocument();
  });

  it("no consulta métricas para una cuenta sin permisos internos", async () => {
    vi.mocked(obtenerSesionActual).mockResolvedValue(CLIENTE);

    render(<PanelOperativo />);

    expect(
      await screen.findByRole("heading", {
        name: "Acceso operativo restringido",
      }),
    ).toBeInTheDocument();
    expect(obtenerResumenComercial).not.toHaveBeenCalled();
  });

  it("permite reintentar cuando falla la carga del reporte", async () => {
    const user = userEvent.setup();
    vi.mocked(obtenerSesionActual).mockResolvedValue(OPERADOR);
    vi.mocked(obtenerResumenComercial)
      .mockRejectedValueOnce(new Error("Servicio no disponible"))
      .mockResolvedValueOnce(RESUMEN);

    render(<PanelOperativo />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Servicio no disponible",
    );
    await user.click(screen.getByRole("button", { name: "Reintentar" }));

    await waitFor(() => expect(obtenerResumenComercial).toHaveBeenCalledTimes(2));
    expect(
      await screen.findByRole("heading", { name: "Buen día, Omar" }),
    ).toBeInTheDocument();
  });
});
