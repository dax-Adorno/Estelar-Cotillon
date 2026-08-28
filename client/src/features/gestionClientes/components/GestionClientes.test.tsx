import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { obtenerSesionActual } from "../../auth/authApi";
import type { UsuarioActual } from "../../auth/types";
import { actualizarPerfil, listarClientes } from "../gestionClientesApi";
import type { ClienteGestion } from "../types";
import { GestionClientes } from "./GestionClientes";

vi.mock("../../auth/authApi", () => ({
  cerrarSesion: vi.fn(),
  obtenerSesionActual: vi.fn(),
}));

vi.mock("../gestionClientesApi", () => ({
  actualizarPerfil: vi.fn(),
  listarClientes: vi.fn(),
}));

const ADMIN: UsuarioActual = {
  id: 1,
  email: "admin@estelart.test",
  nombre: "Ana",
  apellido: "Admin",
  rol: "admin",
  mayorista_aprobado: true,
};

const MAYORISTA: ClienteGestion = {
  id: 7,
  nombre: "María",
  apellido: "López",
  razon_social: "Fiestas del Sol SRL",
  tipo_cliente: "mayorista",
  email: "mayorista@example.com",
  telefono: "",
  whatsapp: "0981000000",
  documento: "",
  cuit: "80012345-6",
  direccion: "Av. Principal 123",
  ciudad: "Asunción",
  provincia: "Capital",
  notas: "",
  activo: true,
  pedidos_total: 4,
  total_comprado: "250000.00",
  ultimo_pedido_en: "2026-08-28T10:00:00-03:00",
  perfil_id: 9,
  rol: "cliente_mayorista",
  mayorista_aprobado: false,
  creado_en: "2026-08-01T10:00:00-03:00",
  actualizado_en: "2026-08-28T10:00:00-03:00",
};

const pagina = { count: 1, next: null, previous: null, results: [MAYORISTA] };

describe("GestionClientes", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(obtenerSesionActual).mockResolvedValue(ADMIN);
    vi.mocked(listarClientes).mockResolvedValue(pagina);
    vi.mocked(actualizarPerfil).mockResolvedValue({});
  });

  it("muestra actividad y ficha comercial de un cliente", async () => {
    const user = userEvent.setup();
    render(<GestionClientes />);
    await user.click(await screen.findByRole("button", { name: /Fiestas del Sol SRL/ }));

    const ficha = screen.getByRole("complementary");
    expect(within(ficha).getByRole("heading", { name: "Fiestas del Sol SRL" })).toBeInTheDocument();
    expect(within(ficha).getByText("mayorista@example.com")).toBeInTheDocument();
    expect(within(ficha).getByText("80012345-6")).toBeInTheDocument();
    expect(screen.getByText("4 pedidos")).toBeInTheDocument();
    expect(within(ficha).getByRole("link", { name: "Ver historial de pedidos" })).toHaveAttribute("href", "/panel/pedidos?search=mayorista%40example.com");
  });

  it("permite a un administrador aprobar una cuenta mayorista", async () => {
    const user = userEvent.setup();
    render(<GestionClientes />);
    await user.click(await screen.findByRole("button", { name: /Fiestas del Sol SRL/ }));
    await user.click(screen.getByRole("button", { name: "Aprobar cuenta mayorista" }));

    await waitFor(() => expect(actualizarPerfil).toHaveBeenCalledWith(9, { mayorista_aprobado: true }));
    expect(await screen.findByRole("status")).toHaveTextContent("Perfil y permisos actualizados correctamente.");
  });

  it("envía segmentación y orden a la API", async () => {
    const user = userEvent.setup();
    render(<GestionClientes />);
    await screen.findByText("Fiestas del Sol SRL");
    await user.type(screen.getByRole("searchbox", { name: "Buscar clientes" }), "Fiestas");
    await user.selectOptions(screen.getByRole("combobox", { name: "Filtrar por tipo de cliente" }), "mayorista");
    await user.selectOptions(screen.getByRole("combobox", { name: "Filtrar por estado de cuenta" }), "mayorista_pendiente");
    await user.selectOptions(screen.getByRole("combobox", { name: "Ordenar clientes" }), "-total_comprado");
    await user.click(screen.getByRole("button", { name: "Aplicar filtros" }));

    await waitFor(() => expect(listarClientes).toHaveBeenLastCalledWith({
      search: "Fiestas",
      tipo_cliente: "mayorista",
      cuenta: "mayorista_pendiente",
      ordering: "-total_comprado",
      page: 1,
    }));
  });

  it("mantiene al operador en modo consulta", async () => {
    const user = userEvent.setup();
    vi.mocked(obtenerSesionActual).mockResolvedValue({ ...ADMIN, rol: "operador" });
    render(<GestionClientes />);
    await user.click(await screen.findByRole("button", { name: /Fiestas del Sol SRL/ }));

    expect(screen.getByText("Vista de consulta. Las aprobaciones mayoristas requieren un administrador.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Aprobar cuenta mayorista" })).not.toBeInTheDocument();
  });

  it("bloquea clientes antes de consultar la cartera interna", async () => {
    vi.mocked(obtenerSesionActual).mockResolvedValue({ ...ADMIN, rol: "cliente_minorista" });
    render(<GestionClientes />);

    expect(await screen.findByRole("heading", { name: "Acceso operativo restringido" })).toBeInTheDocument();
    expect(listarClientes).not.toHaveBeenCalled();
  });
});
