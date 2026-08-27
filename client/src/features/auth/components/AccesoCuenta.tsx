import { useState, type FormEvent } from "react";

import {
  cerrarSesion,
  iniciarSesion,
  registrarMayorista,
  solicitarRestablecimiento,
} from "../authApi";
import type { RegistroMayoristaPayload, UsuarioActual } from "../types";

interface AccesoCuentaProps {
  cargandoSesion: boolean;
  onSesionChange: (usuario: UsuarioActual | null) => void;
  usuario: UsuarioActual | null;
}

type ModoAcceso = "login" | "registro" | "recuperacion";

const NOMBRES_ROL: Record<UsuarioActual["rol"], string> = {
  cliente_minorista: "Cliente minorista",
  cliente_mayorista: "Cliente mayorista",
  operador: "Operador",
  admin: "Administrador",
};

const INPUT_CLASS =
  "mt-1 w-full rounded-xl border border-[#3B3B3B]/20 bg-white px-4 py-3 text-sm outline-none transition focus:border-[#C41D85] focus:ring-2 focus:ring-[#C41D85]/15";

function mensajeError(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "No se pudo completar la operación.";
}

export function AccesoCuenta({
  cargandoSesion,
  onSesionChange,
  usuario,
}: AccesoCuentaProps) {
  const [modo, setModo] = useState<ModoAcceso>("login");
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);

  function cambiarModo(nuevoModo: ModoAcceso): void {
    setModo(nuevoModo);
    setError(null);
    setMensaje(null);
  }

  async function manejarLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setProcesando(true);
    setError(null);
    setMensaje(null);

    try {
      const sesion = await iniciarSesion(
        String(formData.get("email") ?? ""),
        String(formData.get("password") ?? ""),
      );
      onSesionChange(sesion);
    } catch (unknownError) {
      setError(mensajeError(unknownError));
    } finally {
      setProcesando(false);
    }
  }

  async function manejarRegistro(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const payload: RegistroMayoristaPayload = {
      nombre: String(formData.get("nombre") ?? ""),
      apellido: String(formData.get("apellido") ?? ""),
      email: String(formData.get("email") ?? ""),
      whatsapp: String(formData.get("whatsapp") ?? ""),
      tipo_cliente: "mayorista",
      razon_social: String(formData.get("razon_social") ?? ""),
      cuit: String(formData.get("cuit") ?? ""),
      password: String(formData.get("password") ?? ""),
      password_confirmacion: String(
        formData.get("password_confirmacion") ?? "",
      ),
    };

    setProcesando(true);
    setError(null);
    setMensaje(null);
    try {
      const response = await registrarMayorista(payload);
      setMensaje(response.detalle);
      form.reset();
    } catch (unknownError) {
      setError(mensajeError(unknownError));
    } finally {
      setProcesando(false);
    }
  }

  async function manejarRecuperacion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setProcesando(true);
    setError(null);
    setMensaje(null);
    try {
      const response = await solicitarRestablecimiento(
        String(formData.get("email") ?? ""),
      );
      setMensaje(response.detalle);
    } catch (unknownError) {
      setError(mensajeError(unknownError));
    } finally {
      setProcesando(false);
    }
  }

  async function manejarLogout(): Promise<void> {
    setProcesando(true);
    setError(null);
    try {
      await cerrarSesion();
      onSesionChange(null);
    } catch (unknownError) {
      setError(mensajeError(unknownError));
    } finally {
      setProcesando(false);
    }
  }

  if (cargandoSesion) {
    return (
      <p className="rounded-2xl bg-white/85 p-5 text-sm font-semibold" role="status">
        Comprobando sesión segura...
      </p>
    );
  }

  if (usuario) {
    const esInterno = ["operador", "admin"].includes(usuario.rol);
    return (
      <div className="rounded-3xl bg-white/90 p-6 shadow-sm">
        <p className="text-xs font-black uppercase tracking-wide text-[#1D883F]">
          Sesión activa
        </p>
        <h3 className="mt-2 text-2xl font-black text-[#3B3B3B]">
          {usuario.nombre || usuario.email}
        </h3>
        <p className="mt-1 text-sm text-[#3B3B3B]/70">{usuario.email}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="rounded-full bg-[#1D883F]/10 px-3 py-2 text-xs font-black text-[#1D883F]">
            {NOMBRES_ROL[usuario.rol]}
          </span>
          {usuario.rol === "cliente_mayorista" && (
            <span className="rounded-full bg-[#FFBA1F]/20 px-3 py-2 text-xs font-black text-[#3B3B3B]">
              {usuario.mayorista_aprobado
                ? "Mayorista aprobado"
                : "Aprobación pendiente"}
            </span>
          )}
        </div>
        <p className="mt-5 rounded-2xl bg-[#FFEEDC] p-4 text-sm text-[#3B3B3B]/75">
          {esInterno
            ? "Tu cuenta tiene acceso interno. El siguiente módulo habilitará el panel operativo sobre estos permisos."
            : "Ya puedes comprar con una identidad verificada y consultar tus pedidos desde tu cuenta."}
        </p>
        {error && (
          <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm font-bold text-red-700" role="alert">
            {error}
          </p>
        )}
        <button
          className="mt-5 rounded-xl border border-[#3B3B3B]/20 px-4 py-3 text-sm font-black transition hover:bg-[#FFEEDC] disabled:opacity-50"
          disabled={procesando}
          onClick={() => void manejarLogout()}
          type="button"
        >
          {procesando ? "Cerrando..." : "Cerrar sesión"}
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-3xl bg-white/90 p-5 shadow-sm">
      <div className="grid grid-cols-2 gap-2 rounded-2xl bg-[#FFEEDC] p-1">
        <button
          className={`rounded-xl px-3 py-2 text-sm font-black transition ${
            modo === "login" ? "bg-white text-[#1D883F] shadow-sm" : ""
          }`}
          onClick={() => cambiarModo("login")}
          type="button"
        >
          Ingresar
        </button>
        <button
          className={`rounded-xl px-3 py-2 text-sm font-black transition ${
            modo === "registro" ? "bg-white text-[#C41D85] shadow-sm" : ""
          }`}
          onClick={() => cambiarModo("registro")}
          type="button"
        >
          Registro mayorista
        </button>
      </div>

      {modo === "login" && (
        <form className="mt-5 grid gap-4" onSubmit={(event) => void manejarLogin(event)}>
          <label className="text-sm font-bold">
            Correo electrónico
            <input className={INPUT_CLASS} name="email" required type="email" />
          </label>
          <label className="text-sm font-bold">
            Contraseña
            <input
              autoComplete="current-password"
              className={INPUT_CLASS}
              minLength={8}
              name="password"
              required
              type="password"
            />
          </label>
          <button
            className="rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white transition hover:bg-[#FF6515] disabled:opacity-50"
            disabled={procesando}
            type="submit"
          >
            {procesando ? "Ingresando..." : "Iniciar sesión"}
          </button>
          <button
            className="text-sm font-bold text-[#C41D85] underline-offset-4 hover:underline"
            onClick={() => cambiarModo("recuperacion")}
            type="button"
          >
            Olvidé mi contraseña
          </button>
        </form>
      )}

      {modo === "registro" && (
        <form className="mt-5 grid gap-4 sm:grid-cols-2" onSubmit={(event) => void manejarRegistro(event)}>
          <label className="text-sm font-bold">
            Nombre
            <input className={INPUT_CLASS} name="nombre" required />
          </label>
          <label className="text-sm font-bold">
            Apellido
            <input className={INPUT_CLASS} name="apellido" />
          </label>
          <label className="text-sm font-bold sm:col-span-2">
            Correo electrónico
            <input className={INPUT_CLASS} name="email" required type="email" />
          </label>
          <label className="text-sm font-bold">
            WhatsApp
            <input className={INPUT_CLASS} name="whatsapp" required type="tel" />
          </label>
          <label className="text-sm font-bold">
            CUIT / identificador fiscal
            <input className={INPUT_CLASS} name="cuit" required />
          </label>
          <label className="text-sm font-bold sm:col-span-2">
            Razón social
            <input className={INPUT_CLASS} name="razon_social" required />
          </label>
          <label className="text-sm font-bold">
            Contraseña
            <input
              autoComplete="new-password"
              className={INPUT_CLASS}
              minLength={8}
              name="password"
              required
              type="password"
            />
          </label>
          <label className="text-sm font-bold">
            Confirmar contraseña
            <input
              autoComplete="new-password"
              className={INPUT_CLASS}
              minLength={8}
              name="password_confirmacion"
              required
              type="password"
            />
          </label>
          <button
            className="rounded-xl bg-[#C41D85] px-5 py-3 font-black text-white transition hover:opacity-90 disabled:opacity-50 sm:col-span-2"
            disabled={procesando}
            type="submit"
          >
            {procesando ? "Enviando..." : "Solicitar cuenta mayorista"}
          </button>
        </form>
      )}

      {modo === "recuperacion" && (
        <form className="mt-5 grid gap-4" onSubmit={(event) => void manejarRecuperacion(event)}>
          <p className="text-sm text-[#3B3B3B]/70">
            Ingresa tu correo. La respuesta será la misma exista o no la cuenta.
          </p>
          <label className="text-sm font-bold">
            Correo electrónico
            <input className={INPUT_CLASS} name="email" required type="email" />
          </label>
          <button
            className="rounded-xl bg-[#C41D85] px-5 py-3 font-black text-white disabled:opacity-50"
            disabled={procesando}
            type="submit"
          >
            {procesando ? "Enviando..." : "Enviar instrucciones"}
          </button>
          <button
            className="text-sm font-bold text-[#1D883F]"
            onClick={() => cambiarModo("login")}
            type="button"
          >
            Volver al ingreso
          </button>
        </form>
      )}

      {error && (
        <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm font-bold text-red-700" role="alert">
          {error}
        </p>
      )}
      {mensaje && (
        <p className="mt-4 rounded-xl bg-green-50 p-3 text-sm font-bold text-green-800" role="status">
          {mensaje}
        </p>
      )}
    </div>
  );
}
