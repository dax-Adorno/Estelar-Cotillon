import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App.tsx";
import { AuthCallback } from "./features/auth/components/AuthCallback.tsx";
import { PanelOperativo } from "./features/reportes/components/PanelOperativo.tsx";
import "./index.css";

const esRutaAutenticacion = [
  "/verificar-email",
  "/restablecer-password",
].some((path) => window.location.pathname.endsWith(path));
const esPanelOperativo = window.location.pathname.endsWith("/panel");

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {esRutaAutenticacion ? (
      <AuthCallback />
    ) : esPanelOperativo ? (
      <PanelOperativo />
    ) : (
      <App />
    )}
  </StrictMode>,
);
