const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(
  /\/$/,
  "",
);

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

function firstErrorMessage(value: unknown): string | null {
  if (typeof value === "string") {
    return value;
  }

  if (Array.isArray(value)) {
    return value.map(firstErrorMessage).find(Boolean) ?? null;
  }

  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return (
      firstErrorMessage(record.detalle) ??
      firstErrorMessage(record.detail) ??
      Object.values(record).map(firstErrorMessage).find(Boolean) ??
      null
    );
  }

  return null;
}

async function getErrorMessage(response: Response): Promise<string> {
  const data: unknown = await response.json().catch(() => null);
  return firstErrorMessage(data) ?? `Error HTTP ${response.status}`;
}

async function ensureCsrfToken(): Promise<string> {
  const response = await fetch(buildApiUrl("/auth/csrf/"), {
    credentials: "include",
  });
  if (!response.ok) {
    throw new ApiError(await getErrorMessage(response), response.status);
  }

  const data = (await response.json()) as { csrfToken?: unknown };
  if (typeof data.csrfToken !== "string" || data.csrfToken.length === 0) {
    throw new ApiError("No se pudo iniciar una sesión segura.", 500);
  }

  return data.csrfToken;
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);

  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    headers.set("X-CSRFToken", await ensureCsrfToken());
  }
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(buildApiUrl(path), {
    ...init,
    method,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    throw new ApiError(await getErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function getApi<T>(path: string): Promise<T> {
  return apiRequest<T>(path);
}
