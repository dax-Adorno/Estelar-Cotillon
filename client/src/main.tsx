import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App.tsx";
import { AuthCallback } from "./features/auth/components/AuthCallback.tsx";
import "./index.css";

const esRutaAutenticacion = [
  "/verificar-email",
  "/restablecer-password",
].some((path) => window.location.pathname.endsWith(path));

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {esRutaAutenticacion ? <AuthCallback /> : <App />}
  </StrictMode>,
);
