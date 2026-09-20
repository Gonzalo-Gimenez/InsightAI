export interface VentaItem {
  producto: string;
  categoria: string;
  region: string;
  ventas: number;
}

export interface MetricsResponse {
  total_ventas: number;
  promedio_ventas: number;
  venta_maxima: VentaItem;
  venta_minima: VentaItem;
  ventas_por_categoria: Record<string, number>;
}

export interface ChatResponse {
  answer: string;
  tools: ToolResult[];
}

export interface ToolResult {
  name: string;
  arguments: Record<string, unknown>;
  result: unknown;
}

function apiBase(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!raw) return "";
  return raw.replace(/\/$/, "");
}

function apiUrl(path: string): string {
  const base = apiBase();
  return base ? `${base}${path}` : path;
}

export async function getMetrics(): Promise<MetricsResponse> {
  const res = await fetch(apiUrl("/api/v1/metrics"));
  if (!res.ok) {
    throw new Error("metrics fetch failed");
  }
  return res.json() as Promise<MetricsResponse>;
}

export async function askQuestion(question: string): Promise<ChatResponse> {
  const res = await fetch(apiUrl("/api/v1/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    throw new Error("chat request failed");
  }
  return res.json() as Promise<ChatResponse>;
}
