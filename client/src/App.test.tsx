import { render, screen } from "@testing-library/react";
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
              nombre: "Limpiapipas surtidos",
              slug: "limpiapipas-surtidos",
              descripcion: "",
              precio_minorista: "1500.00",
              precio_mayorista: "1200.00",
              cantidad_minima_mayorista: 10,
              stock: 50,
              activo: true,
              destacado: true,
            },
          ]),
        );
      }

      if (url.includes("/promociones/")) {
        return Promise.resolve(
          crearRespuesta([
            {
              id: 1,
              nombre: "Promo vigente",
              slug: "promo-vigente",
              descripcion: "",
              tipo_promocion: "porcentaje",
              porcentaje_descuento: "10.00",
              monto_descuento: null,
              compra_minima: null,
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

  it("deberia mostrar la landing principal de ESTELART", async () => {
    render(<App />);

    expect(screen.getByText("ESTELART Platform")).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /plataforma comercial para cotillón/i,
      }),
    ).toBeInTheDocument();

    expect(await screen.findByText("Limpiapipas surtidos")).toBeInTheDocument();
    expect(screen.getByText("Promo vigente")).toBeInTheDocument();
  });
});
