export interface KpiBlock {
  ingresos?: number | null;
  margen_pct?: number | null;
  ticket?: number | null;
  unidades?: number | null;
  deltas?: Record<string, number | null> | null;
}

export interface ChartSpec {
  id: string;
  type: "line" | "bar" | "table" | "pie";
  title: string;
  data: unknown[];
}

export interface WorkspaceView {
  period: { from?: string | null; to?: string | null };
  coverage?: { from?: string | null; to?: string | null } | null;
  kpis: KpiBlock;
  charts: ChartSpec[];
  source?: "default" | "query" | string | null;
}

export interface MetricsResponse {
  view: WorkspaceView;
}

export interface ToolResult {
  name: string;
  arguments: Record<string, unknown>;
  result: unknown;
  sql?: string | null;
}

export interface ChatResponse {
  answer: string;
  tools: ToolResult[];
  view?: WorkspaceView | null;
}

export interface HistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
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

function flattenDetail(detail: unknown): string | undefined {
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return null;
      })
      .filter((part): part is string => Boolean(part));
    return parts.length ? parts.join(". ") : undefined;
  }
  if (detail && typeof detail === "object" && "msg" in detail) {
    return String((detail as { msg: unknown }).msg);
  }
  return undefined;
}

function chatErrorMessage(status: number, detail?: unknown): string {
  if (status === 401) {
    return "Error de autenticación con el servicio de IA.";
  }
  if (status === 429) {
    return "Límite de solicitudes alcanzado. Probá de nuevo en unos minutos.";
  }
  if (status === 503) {
    return "La API o la base de datos no están disponibles. ¿Corriste el seed Nortec?";
  }
  const flattened = flattenDetail(detail);
  if (flattened) {
    return flattened;
  }
  return "No se pudo obtener una respuesta del servidor.";
}

function metricsErrorMessage(): string {
  if (apiBase()) {
    return "No se pudieron cargar las métricas. Verificá que la API esté en línea.";
  }
  return "No se pudieron cargar las métricas. Iniciá el backend local antes de usar el frontend.";
}

export async function getHealth(): Promise<{ status: string; database?: string }> {
  const res = await fetch(apiUrl("/api/v1/health"));
  if (!res.ok) {
    return { status: "degraded" };
  }
  return res.json() as Promise<{ status: string; database?: string }>;
}

export async function getMetrics(): Promise<MetricsResponse> {
  const res = await fetch(apiUrl("/api/v1/metrics"));
  if (!res.ok) {
    throw new ApiError(metricsErrorMessage(), res.status);
  }
  return res.json() as Promise<MetricsResponse>;
}

export async function askQuestion(
  question: string,
  history: HistoryMessage[] = [],
): Promise<ChatResponse> {
  const res = await fetch(apiUrl("/api/v1/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });

  if (!res.ok) {
    let detail: unknown;
    try {
      const body = (await res.json()) as { detail?: unknown };
      detail = body.detail;
    } catch {
      detail = undefined;
    }
    throw new ApiError(chatErrorMessage(res.status, detail), res.status);
  }

  const payload = (await res.json()) as ChatResponse;
  return {
    ...payload,
    answer: typeof payload.answer === "string" ? payload.answer : "",
    tools: Array.isArray(payload.tools) ? payload.tools : [],
  };
}