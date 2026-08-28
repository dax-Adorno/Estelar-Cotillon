import { afterEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "./api";

function respuestaJson(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("apiRequest", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("deja que el navegador defina el boundary de multipart", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(respuestaJson({ csrfToken: "csrf-seguro" }))
      .mockResolvedValueOnce(respuestaJson({ id: 7 }, 201));
    vi.stubGlobal("fetch", fetchMock);
    const formData = new FormData();
    formData.set("imagen", new File(["imagen"], "producto.webp", { type: "image/webp" }));

    await apiRequest("/gestion/imagenes-producto/", {
      method: "POST",
      body: formData,
    });

    const [, request] = fetchMock.mock.calls[1];
    const headers = new Headers(request?.headers);
    expect(headers.get("Content-Type")).toBeNull();
    expect(headers.get("X-CSRFToken")).toBe("csrf-seguro");
  });

  it("mantiene JSON como formato predeterminado para escrituras comunes", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(respuestaJson({ csrfToken: "csrf-seguro" }))
      .mockResolvedValueOnce(respuestaJson({ id: 3 }, 201));
    vi.stubGlobal("fetch", fetchMock);

    await apiRequest("/gestion/productos/", {
      method: "POST",
      body: JSON.stringify({ nombre: "Producto" }),
    });

    const [, request] = fetchMock.mock.calls[1];
    const headers = new Headers(request?.headers);
    expect(headers.get("Content-Type")).toBe("application/json");
  });
});
