import { useEffect, useState, type FormEvent } from "react";

import {
  confirmarRestablecimiento,
  verificarEmail,
} from "../authApi";

const INPUT_CLASS =
  "mt-1 w-full rounded-xl border border-[#3B3B3B]/20 bg-white px-4 py-3 outline-none focus:border-[#C41D85] focus:ring-2 focus:ring-[#C41D85]/15";

function obtenerCredencialesUrl(): { uid: string; token: string } {
  const params = new URLSearchParams(window.location.search);
  return {
    uid: params.get("uid") ?? "",
    token: params.get("token") ?? "",
  };
}

function mensajeError(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "No se pudo validar el enlace.";
}

export function AuthCallback() {
  const esVerificacion = window.location.pathname.endsWith("/verificar-email");
  const esRestablecimiento = window.location.pathname.endsWith(
    "/restablecer-password",
  );
  const credencialesIniciales = obtenerCredencialesUrl();
  const enlaceVerificacionIncompleto =
    esVerificacion &&
    (!credencialesIniciales.uid || !credencialesIniciales.token);
  const [procesando, setProcesando] = useState(
    esVerificacion && !enlaceVerificacionIncompleto,
  );
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(
    enlaceVerificacionIncompleto
      ? "El enlace de verificación está incompleto."
      : null,
  );

  useEffect(() => {
    if (!esVerificacion) {
      return;
    }

    const { uid, token } = obtenerCredencialesUrl();
    if (!uid || !token) {
      return;
    }

    verificarEmail(uid, token)
      .then((response) => setMensaje(response.detalle))
      .catch((unknownError: unknown) => setError(mensajeError(unknownError)))
      .finally(() => setProcesando(false));
  }, [esVerificacion]);

  async function manejarRestablecimiento(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const { uid, token } = obtenerCredencialesUrl();
    const formData = new FormData(form);

    if (!uid || !token) {
      setError("El enlace de recuperación está incompleto.");
      return;
    }

    setProcesando(true);
    setError(null);
    setMensaje(null);
    try {
      const response = await confirmarRestablecimiento(
        uid,
        token,
        String(formData.get("password") ?? ""),
        String(formData.get("password_confirmacion") ?? ""),
      );
      setMensaje(response.detalle);
      form.reset();
    } catch (unknownError) {
      setError(mensajeError(unknownError));
    } finally {
      setProcesando(false);
    }
  }

  if (!esVerificacion && !esRestablecimiento) {
    return null;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#FFEEDC] px-6 py-12 text-[#3B3B3B]">
      <section className="w-full max-w-lg rounded-3xl bg-white p-7 shadow-sm ring-1 ring-[#FFBA1F]/40">
        <img alt="ESTELART" className="h-14 w-auto" src="/brand/estelart-logo.svg" />
        <p className="mt-6 text-sm font-black uppercase tracking-wide text-[#C41D85]">
          Acceso seguro
        </p>
        <h1 className="mt-2 text-3xl font-black">
          {esVerificacion ? "Verificación de correo" : "Nueva contraseña"}
        </h1>

        {esRestablecimiento && !mensaje && (
          <form className="mt-6 grid gap-4" onSubmit={(event) => void manejarRestablecimiento(event)}>
            <label className="text-sm font-bold">
              Nueva contraseña
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
              className="rounded-xl bg-[#1D883F] px-5 py-3 font-black text-white disabled:opacity-50"
              disabled={procesando}
              type="submit"
            >
              {procesando ? "Actualizando..." : "Actualizar contraseña"}
            </button>
          </form>
        )}

        {procesando && esVerificacion && (
          <p className="mt-6 rounded-xl bg-[#FFEEDC] p-4 font-semibold" role="status">
            Validando enlace...
          </p>
        )}
        {mensaje && (
          <p className="mt-6 rounded-xl bg-green-50 p-4 font-bold text-green-800" role="status">
            {mensaje}
          </p>
        )}
        {error && (
          <p className="mt-6 rounded-xl bg-red-50 p-4 font-bold text-red-700" role="alert">
            {error}
          </p>
        )}

        <a
          className="mt-6 inline-flex rounded-xl border border-[#3B3B3B]/20 px-4 py-3 text-sm font-black hover:bg-[#FFEEDC]"
          href="/#acceso"
        >
          Volver a ESTELART
        </a>
      </section>
    </main>
  );
}
