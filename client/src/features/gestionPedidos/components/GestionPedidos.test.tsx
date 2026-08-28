import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { obtenerSesionActual } from "../../auth/authApi";
import type { UsuarioActual } from "../../auth/types";
import {
  cambiarEstadoPedido,
  listarPedidos,
  obtenerPedido,
} from "../gestionPedidosApi";
import type { PedidoDetalle, PedidoResumen } from "../types";
import { GestionPedidos } from "./GestionPedidos";

vi.mock("../../auth/authApi", () => ({
  cerrarSesion: vi.fn(),
  obtenerSesionActual: vi.fn(),
}));

vi.mock("../gestionPedidosApi", () => ({
  cambiarEstadoPago: vi.fn(),
  cambiarEstadoPedido: vi.fn(),
  listarPedidos: vi.fn(),
  obtenerPedido: vi.fn(),
}));

const OPERADOR: UsuarioActual = {
  id: 12,
  email: "operador@estelart.test",
  nombre: "Omar",
  apellido: "Operador",
  rol: "operador",
  mayorista_aprobado: false,
};

const RESUMEN: PedidoResumen = {
  id: 21,
  cliente: 7,
  cliente_nombre: "María López",
  cliente_email: "maria@example.com",
  codigo: "PED-2026-0021",
  estado: "pendiente",
  estado_pago: "pendiente",
  canal_venta: "web",
  total: "20000.00",
  promocion_nombre: "",
  cantidad_items: 1,
  cantidad_unidades: 2,
  creado_en: "2026-08-28T10:00:00-03:00",
  actualizado_en: "2026-08-28T10:00:00-03:00",
};

const DETALLE: PedidoDetalle = {
  id: 21,
  cliente: 7,
  cliente_nombre: "María López",
  codigo: "PED-2026-0021",
  estado: "pendiente",
  estado_pago: "pendiente",
  canal_venta: "web",
  subtotal: "20000.00",
  descuento: "0.00",
  total: "20000.00",
  promocion_aplicada: null,
  promocion_nombre: "",
  notas: "Entregar por la tarde",
  detalles: [{
    id: 31,
    pedido: 21,
    producto: 8,
    producto_nombre: "Guirnalda premium",
    producto_sku: "GUI-008",
    cantidad: 2,
    precio_unitario: "10000.00",
    subtotal: "20000.00",
    creado_en: "2026-08-28T10:00:00-03:00",
    actualizado_en: "2026-08-28T10:00:00-03:00",
  }],
  eventos: [],
  creado_en: "2026-08-28T10:00:00-03:00",
  actualizado_en: "2026-08-28T10:00:00-03:00",
};

const pagina = { count: 1, next: null, previous: null, results: [RESUMEN] };

describe("GestionPedidos", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(obtenerSesionActual).mockResolvedValue(OPERADOR);
    vi.mocked(listarPedidos).mockResolvedValue(pagina);
    vi.mocked(obtenerPedido).mockResolvedValue(DETALLE);
    vi.mocked(cambiarEstadoPedido).mockResolvedValue({ ...DETALLE, estado: "confirmado" });
  });

  it("presenta una bandeja operativa con datos accionables", async () => {
    render(<GestionPedidos />);

    expect(await screen.findByRole("heading", { name: "Pedidos y cobros" })).toBeInTheDocument();
    expect(screen.getByText("PED-2026-0021")).toBeInTheDocument();
    expect(screen.getByText("María López")).toBeInTheDocument();
    expect(screen.getByText("2 unidades · 1 producto")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Catálogo" })).toHaveAttribute("href", "/panel/catalogo");
  });

  it("envía búsqueda, filtros, fechas y orden al listado", async () => {
    const user = userEvent.setup();
    render(<GestionPedidos />);
    await screen.findByText("PED-2026-0021");

    await user.type(screen.getByRole("searchbox", { name: "Buscar pedidos" }), "María");
    await user.selectOptions(screen.getByRole("combobox", { name: "Filtrar por estado del pedido" }), "pendiente");
    await user.selectOptions(screen.getByRole("combobox", { name: "Filtrar por estado del pago" }), "pendiente");
    await user.selectOptions(screen.getByRole("combobox", { name: "Filtrar por canal" }), "web");
    await user.selectOptions(screen.getByRole("combobox", { name: "Ordenar pedidos" }), "-total");
    await user.click(screen.getByRole("button", { name: "Aplicar filtros" }));

    await waitFor(() => expect(listarPedidos).toHaveBeenLastCalledWith(expect.objectContaining({
      search: "María",
      estado: "pendiente",
      estado_pago: "pendiente",
      canal_venta: "web",
      ordering: "-total",
      page: 1,
    })));
  });

  it("confirma un pedido con comentario auditable", async () => {
    const user = userEvent.setup();
    render(<GestionPedidos />);
    await screen.findByText("PED-2026-0021");
    await user.click(screen.getByRole("button", { name: "Ver y gestionar" }));

    const panel = await screen.findByRole("region", { name: "Detalle del pedido PED-2026-0021" });
    expect(within(panel).getByRole("heading", { name: "PED-2026-0021", level: 2 })).toBeInTheDocument();
    expect(within(panel).getByText("Guirnalda premium")).toBeInTheDocument();
    await user.selectOptions(within(panel).getByRole("combobox", { name: "Nuevo estado del pedido" }), "confirmado");
    await user.type(within(panel).getByRole("textbox", { name: "Comentario del estado" }), "Stock verificado");
    await user.click(within(panel).getByRole("button", { name: "Aplicar estado" }));

    await waitFor(() => expect(cambiarEstadoPedido).toHaveBeenCalledWith(21, "confirmado", "Stock verificado"));
  });

  it("exige reembolso antes de ofrecer la cancelación de un pedido cobrado", async () => {
    vi.mocked(obtenerPedido).mockResolvedValue({ ...DETALLE, estado: "confirmado", estado_pago: "pagado" });
    const user = userEvent.setup();
    render(<GestionPedidos />);
    await screen.findByText("PED-2026-0021");
    await user.click(screen.getByRole("button", { name: "Ver y gestionar" }));

    const panel = await screen.findByRole("region", { name: "Detalle del pedido PED-2026-0021" });
    expect(within(panel).getByText("Para cancelar este pedido primero registra el reembolso.")).toBeInTheDocument();
    const selectorEstado = within(panel).getByRole("combobox", { name: "Nuevo estado del pedido" });
    const selectorPago = within(panel).getByRole("combobox", { name: "Nuevo estado del pago" });
    expect(within(selectorEstado).getByRole("option", { name: "Entregado" })).toBeInTheDocument();
    expect(within(selectorEstado).queryByRole("option", { name: "Cancelado" })).not.toBeInTheDocument();
    expect(within(selectorPago).getByRole("option", { name: "Reembolsado" })).toBeInTheDocument();
  });

  it("bloquea clientes antes de consultar pedidos internos", async () => {
    vi.mocked(obtenerSesionActual).mockResolvedValue({ ...OPERADOR, rol: "cliente_minorista" });
    render(<GestionPedidos />);

    expect(await screen.findByRole("heading", { name: "Acceso operativo restringido" })).toBeInTheDocument();
    expect(listarPedidos).not.toHaveBeenCalled();
  });
});
