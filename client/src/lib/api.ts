const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export async function getApi<T>(path: string): Promise<T> {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const response = await fetch(`${API_BASE_URL}${normalizedPath}`);

  if (!response.ok) {
    throw new Error(`Error HTTP ${response.status}`);
  }

  return (await response.json()) as T;
}
