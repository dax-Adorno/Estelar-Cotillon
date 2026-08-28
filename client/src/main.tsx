import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App.tsx";
import { AuthCallback } from "./features/auth/components/AuthCallback.tsx";
import { GestionCatalogo } from "./features/gestionCatalogo/components/GestionCatalogo.tsx";
import { GestionPedidos } from "./features/gestionPedidos/components/GestionPedidos.tsx";
import { PanelOperativo } from "./features/reportes/components/PanelOperativo.tsx";
import "./index.css";

const esRutaAutenticacion = [
  "/verificar-email",
  "/restablecer-password",
].some((path) => window.location.pathname.endsWith(path));
const esPanelOperativo = window.location.pathname.endsWith("/panel");
const esGestionCatalogo = window.location.pathname.endsWith("/panel/catalogo");
const esGestionPedidos = window.location.pathname.endsWith("/panel/pedidos");

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {esRutaAutenticacion ? (
      <AuthCallback />
    ) : esGestionPedidos ? (
      <GestionPedidos />
    ) : esGestionCatalogo ? (
      <GestionCatalogo />
    ) : esPanelOperativo ? (
      <PanelOperativo />
    ) : (
      <App />
    )}
  </StrictMode>,
);
