import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

function crearRespuesta(data: unknown): Response {
  return {
    ok: true,
    json: () => Promise.resolve(data),
  } as Response;
}

describe("App", () => {
  beforeEach(() => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);

      if (url.includes("/categorias/")) {
        return Promise.resolve(
          crearRespuesta([
            {
              id: 1,
              nombre: "Limpiapipas",
              slug: "limpiapipas",
              descripcion: "",
              activa: true,
            },
            {
              id: 2,
              nombre: "Slime y gel",
              slug: "slime-y-gel",
              descripcion: "",
              activa: true,
            },
          ]),
        );
      }

      if (url.includes("/productos/")) {
        return Promise.resolve(
          crearRespuesta([
            {
              id: 1,
              categoria: 1,
              categoria_nombre: "Limpiapipas",
              sku: "LIM-001",
              nombre: "Limpiapipas surtidos 30 cm",
              slug: "limpiapipas-surtidos-30-cm",
              descripcion: "Pack de limpiapipas de colores surtidos.",
              precio_minorista: "1500.00",
              precio_mayorista: "1200.00",
              cantidad_minima_mayorista: 10,
              stock: 180,
              activo: true,
              destacado: true,
            },
            {
              id: 2,
              categoria: 2,
              categoria_nombre: "Slime y gel",
              sku: "SLI-001",
              nombre: "Kit slime colores pastel",
              slug: "kit-slime-colores-pastel",
              descripcion: "Kit creativo para armado de slime.",
              precio_minorista: "8500.00",
              precio_mayorista: "7200.00",
              cantidad_minima_mayorista: 5,
              stock: 35,
              activo: true,
              destacado: true,
            },
            {
              id: 3,
              categoria: 1,
              categoria_nombre: "Limpiapipas",
              sku: "LIM-002",
              nombre: "Limpiapipas metalizados",
              slug: "limpiapipas-metalizados",
              descripcion: "Limpiapipas con terminación metalizada.",
              precio_minorista: "2200.00",
              precio_mayorista: "1750.00",
              cantidad_minima_mayorista: 10,
              stock: 90,
              activo: true,
              destacado: false,
            },
          ]),
        );
      }

      if (url.includes("/promociones/")) {
        return Promise.resolve(
          crearRespuesta([
            {
              id: 1,
              nombre: "Mayorista creativo",
              slug: "mayorista-creativo",
              descripcion: "Beneficio para compras mayoristas.",
              tipo_promocion: "mayorista",
              porcentaje_descuento: "10.00",
              monto_descuento: null,
              compra_minima: "30000.00",
              canal_venta: "todos",
              activa: true,
              vigente: true,
            },
          ]),
        );
      }

      return Promise.resolve(crearRespuesta([]));
    });

    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("deberia mostrar productos y promociones desde la API", async () => {
    render(<App />);

    expect(screen.getByText("ESTELART Platform")).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /catálogo inteligente para cotillón/i,
      }),
    ).toBeInTheDocument();

    expect(
      await screen.findByText("Limpiapipas surtidos 30 cm"),
    ).toBeInTheDocument();

    expect(screen.getByText("Mayorista creativo")).toBeInTheDocument();
  });

  it("deberia filtrar productos por categoria", async () => {
    render(<App />);

    expect(
      await screen.findByText("Limpiapipas surtidos 30 cm"),
    ).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Filtrar por categoría"), {
      target: { value: "2" },
    });

    expect(screen.getByText("Kit slime colores pastel")).toBeInTheDocument();

    expect(
      screen.queryByText("Limpiapipas surtidos 30 cm"),
    ).not.toBeInTheDocument();

    expect(screen.queryByText("Limpiapipas metalizados")).not.toBeInTheDocument();
  });

  it("deberia filtrar solamente productos destacados", async () => {
    render(<App />);

    expect(
      await screen.findByText("Limpiapipas metalizados"),
    ).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("checkbox", {
        name: /solo destacados/i,
      }),
    );

    expect(screen.getByText("Limpiapipas surtidos 30 cm")).toBeInTheDocument();
    expect(screen.getByText("Kit slime colores pastel")).toBeInTheDocument();

    expect(screen.queryByText("Limpiapipas metalizados")).not.toBeInTheDocument();
  });
});
