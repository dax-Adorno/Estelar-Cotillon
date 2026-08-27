import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  cerrarSesion,
  iniciarSesion,
  registrarMayorista,
} from "../authApi";
import type { UsuarioActual } from "../types";
import { AccesoCuenta } from "./AccesoCuenta";

vi.mock("../authApi", () => ({
  cerrarSesion: vi.fn(),
  iniciarSesion: vi.fn(),
  registrarMayorista: vi.fn(),
  solicitarRestablecimiento: vi.fn(),
}));

const USUARIO_OPERADOR: UsuarioActual = {
  id: 7,
  email: "operador@estelart.test",
  nombre: "Olivia",
  apellido: "Operadora",
  rol: "operador",
  mayorista_aprobado: false,
};

describe("AccesoCuenta", () => {
  beforeEach(() => {
    vi.mocked(cerrarSesion).mockReset();
    vi.mocked(iniciarSesion).mockReset();
    vi.mocked(registrarMayorista).mockReset();
  });

  it("inicia sesión y entrega la identidad al contenedor", async () => {
    const user = userEvent.setup();
    const onSesionChange = vi.fn();
    vi.mocked(iniciarSesion).mockResolvedValue(USUARIO_OPERADOR);

    render(
      <AccesoCuenta
        cargandoSesion={false}
        onSesionChange={onSesionChange}
        usuario={null}
      />,
    );

    await user.type(
      screen.getByRole("textbox", { name: /correo electrónico/i }),
      USUARIO_OPERADOR.email,
    );
    await user.type(screen.getByLabelText("Contraseña"), "Clave-segura-2026");
    await user.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    await waitFor(() => {
      expect(iniciarSesion).toHaveBeenCalledWith(
        USUARIO_OPERADOR.email,
        "Clave-segura-2026",
      );
    });
    expect(onSesionChange).toHaveBeenCalledWith(USUARIO_OPERADOR);
  });

  it("envía un registro mayorista completo", async () => {
    const user = userEvent.setup();
    vi.mocked(registrarMayorista).mockResolvedValue({
      detalle: "Revisa tu correo para activar la cuenta.",
    });

    render(
      <AccesoCuenta
        cargandoSesion={false}
        onSesionChange={vi.fn()}
        usuario={null}
      />,
    );

    await user.click(
      screen.getByRole("button", { name: "Registro mayorista" }),
    );
    await user.type(screen.getByLabelText("Nombre"), "Mara");
    await user.type(screen.getByLabelText("Apellido"), "Mayorista");
    await user.type(
      screen.getByRole("textbox", { name: /correo electrónico/i }),
      "mara@negocio.test",
    );
    await user.type(screen.getByLabelText("WhatsApp"), "0981000000");
    await user.type(
      screen.getByLabelText(/CUIT \/ identificador fiscal/i),
      "80000001-0",
    );
    await user.type(screen.getByLabelText("Razón social"), "Mara Cotillón");
    await user.type(screen.getByLabelText("Contraseña"), "Clave-segura-2026");
    await user.type(
      screen.getByLabelText("Confirmar contraseña"),
      "Clave-segura-2026",
    );
    await user.click(
      screen.getByRole("button", { name: "Solicitar cuenta mayorista" }),
    );

    await waitFor(() => expect(registrarMayorista).toHaveBeenCalledOnce());
    expect(registrarMayorista).toHaveBeenCalledWith(
      expect.objectContaining({
        email: "mara@negocio.test",
        tipo_cliente: "mayorista",
        razon_social: "Mara Cotillón",
        cuit: "80000001-0",
      }),
    );
    expect(
      screen.getByText("Revisa tu correo para activar la cuenta."),
    ).toBeInTheDocument();
  });

  it("muestra el rol y permite cerrar una sesión interna", async () => {
    const user = userEvent.setup();
    const onSesionChange = vi.fn();
    vi.mocked(cerrarSesion).mockResolvedValue();

    render(
      <AccesoCuenta
        cargandoSesion={false}
        onSesionChange={onSesionChange}
        usuario={USUARIO_OPERADOR}
      />,
    );

    expect(screen.getByText("Operador")).toBeInTheDocument();
    expect(screen.getByText(/acceso interno/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cerrar sesión" }));

    await waitFor(() => expect(cerrarSesion).toHaveBeenCalledOnce());
    expect(onSesionChange).toHaveBeenCalledWith(null);
  });
});
