import { render, screen } from "@testing-library/react";

import App from "./App";
import { describe, expect, it } from "vitest";

describe("App", () => {
  it("deberia mostrar la landing principal de ESTELART", () => {
    render(<App />);

    expect(screen.getByText("ESTELART Platform")).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: /plataforma comercial para cotillón/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: /ver catálogo/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: /acceso mayoristas/i,
      }),
    ).toBeInTheDocument();
  });
});
