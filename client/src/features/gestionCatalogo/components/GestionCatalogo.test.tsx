import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { obtenerSesionActual } from "../../auth/authApi";
import type { UsuarioActual } from "../../auth/types";
import {
  guardarProducto,
  listarCategoriasGestion,
  listarProductosGestion,
} from "../gestionCatalogoApi";
import type { CategoriaGestion, ProductoGestion } from "../types";
import { GestionCatalogo } from "./GestionCatalogo";

vi.mock("../../auth/authApi", () => ({
  cerrarSesion: vi.fn(),
  obtenerSesionActual: vi.fn(),
}));

vi.mock("../gestionCatalogoApi", () => ({
  actualizarImagenProducto: vi.fn(),
  eliminarImagenProducto: vi.fn(),
  guardarCategoria: vi.fn(),
  guardarProducto: vi.fn(),
  listarCategoriasGestion: vi.fn(),
  listarImagenesProducto: vi.fn(),
  listarProductosGestion: vi.fn(),
  subirImagenProducto: vi.fn(),
}));

const OPERADOR: UsuarioActual = {
  id: 12,
  email: "operador@estelart.test",
  nombre: "Omar",
  apellido: "Operador",
  rol: "operador",
  mayorista_aprobado: false,
};

const CATEGORIA: CategoriaGestion = {
  id: 2,
  nombre: "Globos",
  slug: "globos",
  descripcion: "Globos para fiestas",
  activa: true,
  creada_en: "2026-08-27T12:00:00-03:00",
  actualizada_en: "2026-08-27T12:00:00-03:00",
};

const PRODUCTO: ProductoGestion = {
  id: 8,
  categoria: 2,
  categoria_nombre: "Globos",
  sku: "GLO-008",
  nombre: "Globos pastel",
  slug: "globos-pastel",
  descripcion: "Bolsa de globos pastel",
  precio_minorista: "3500.00",
  precio_mayorista: "2800.00",
  cantidad_minima_mayorista: 5,
  stock: 7,
  activo: true,
  destacado: false,
  cantidad_imagenes: 2,
  creado_en: "2026-08-27T12:00:00-03:00",
  actualizado_en: "2026-08-27T12:00:00-03:00",
};

const pagina = <T,>(results: T[]) => ({ count: results.length, next: null, previous: null, results });

describe("GestionCatalogo", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(obtenerSesionActual).mockResolvedValue(OPERADOR);
    vi.mocked(listarCategoriasGestion).mockResolvedValue(pagina([CATEGORIA]));
    vi.mocked(listarProductosGestion).mockResolvedValue(pagina([PRODUCTO]));
    vi.mocked(guardarProducto).mockResolvedValue(PRODUCTO);
    window.scrollTo = vi.fn();
  });

  it("muestra inventario, precios, stock y navegación al operador", async () => {
    render(<GestionCatalogo />);

    expect(await screen.findByRole("heading", { name: "Catálogo comercial" })).toBeInTheDocument();
    expect(screen.getByText("Globos pastel")).toBeInTheDocument();
    expect(screen.getByText("GLO-008 · Globos")).toBeInTheDocument();
    expect(screen.getByText("7 unidades")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Resumen" })).toHaveAttribute("href", "/panel");
  });

  it("aplica búsqueda y filtros al endpoint de gestión", async () => {
    const user = userEvent.setup();
    render(<GestionCatalogo />);
    await screen.findByText("Globos pastel");

    await user.type(screen.getByRole("searchbox", { name: "Buscar productos" }), "pastel");
    await user.selectOptions(screen.getByRole("combobox", { name: "Filtrar por categoría" }), "2");
    await user.selectOptions(screen.getByRole("combobox", { name: "Filtrar por estado" }), "activos");
    await user.click(screen.getByRole("button", { name: "Filtrar" }));

    await waitFor(() => expect(listarProductosGestion).toHaveBeenLastCalledWith({ search: "pastel", categoria: 2, activo: "true" }));
  });

  it("edita stock y conserva el contrato esperado por la API", async () => {
    const user = userEvent.setup();
    render(<GestionCatalogo />);
    await screen.findByText("Globos pastel");

    await user.click(screen.getByRole("button", { name: "Editar" }));
    const stock = screen.getByRole("spinbutton", { name: "Stock disponible" });
    await user.clear(stock);
    await user.type(stock, "25");
    await user.click(screen.getByRole("button", { name: "Actualizar producto" }));

    await waitFor(() => expect(guardarProducto).toHaveBeenCalledWith(expect.objectContaining({
      categoria: 2,
      sku: "GLO-008",
      stock: 25,
      activo: true,
    }), 8));
    expect(await screen.findByRole("status")).toHaveTextContent("Producto actualizado correctamente.");
  });

  it("bloquea el acceso y no consulta datos para clientes", async () => {
    vi.mocked(obtenerSesionActual).mockResolvedValue({ ...OPERADOR, rol: "cliente_minorista" });
    render(<GestionCatalogo />);

    expect(await screen.findByRole("heading", { name: "Acceso operativo restringido" })).toBeInTheDocument();
    expect(listarCategoriasGestion).not.toHaveBeenCalled();
    expect(listarProductosGestion).not.toHaveBeenCalled();
  });
});
