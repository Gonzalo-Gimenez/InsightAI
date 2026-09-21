"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  askQuestion,
  ApiError,
  type ChatResponse,
  type HistoryMessage,
  type ToolResult,
  type WorkspaceView,
} from "@/lib/api";
import { cn } from "@/lib/cn";

const SUGGESTIONS = [
  "¿Cómo van los ingresos del último mes vs el anterior?",
  "Top 5 productos por margen en AMBA",
  "Mix de ventas online vs tienda",
  "Ticket promedio por región",
];

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  tools: ToolResult[];
}

function messageText(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

function ChatBody({ text }: { text: string }) {
  const cleaned = text
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^\s*[-*]\s+/gm, "• ");
  const parts = cleaned.split(/(\*\*[^*]+\*\*)/g);
  return (
    <p className="whitespace-pre-wrap leading-relaxed">
      {parts.map((part, i) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={i} className="font-medium text-zinc-100">
            {part.slice(2, -2)}
          </strong>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </p>
  );
}

const TOOL_LABELS: Record<string, string> = {
  kpis_periodo: "KPIs del período",
  serie_mensual: "Serie mensual",
  ranking_productos: "Ranking de productos",
  mix_categoria: "Mix por categoría",
  mix_region: "Mix por región",
  mix_canal: "Mix por canal",
  ticket_promedio: "Ticket promedio",
  comparar_periodos: "Comparar períodos",
  consultar_sql: "SQL de solo lectura",
  listar_esquema: "Esquema",
  describir_tabla: "Describir tabla",
};

function ToolEvidence({ tools }: { tools: ToolResult[] }) {
  if (!tools.length) return null;
  return (
    <div className="mt-2 space-y-2" aria-label="Consultas usadas">
      {tools.map((tool, index) => {
        const sql =
          tool.sql ??
          (typeof tool.result === "object" &&
          tool.result !== null &&
          "sql" in (tool.result as Record<string, unknown>)
            ? String((tool.result as { sql: string }).sql)
            : null);
        const label = TOOL_LABELS[tool.name] ?? tool.name;
        return (
          <details
            key={`${tool.name}-${index}`}
            className="rounded-lg border border-zinc-800 bg-zinc-950/80 text-xs"
          >
            <summary className="cursor-pointer px-3 py-2 text-emerald-400/90">
              Consulta: {label}
            </summary>
            {sql ? (
              <pre className="overflow-x-auto border-t border-zinc-800 px-3 py-2 font-mono text-zinc-400">
                {sql}
              </pre>
            ) : (
              <p className="border-t border-zinc-800 px-3 py-2 text-zinc-500">
                Métrica agregada en SQL, sin filas crudas.
              </p>
            )}
          </details>
        );
      })}
    </div>
  );
}

export function CopilotPanel({
  onViewUpdate,
}: {
  onViewUpdate: (view: WorkspaceView) => void;
}) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const el = listRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) {
      inputRef.current?.focus();
    }
  }, [loading]);

  async function sendText(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const history: HistoryMessage[] = messages
      .filter((m) => typeof m.text === "string" && m.text.trim().length > 0)
      .slice(-10)
      .map((m) => ({
        role: m.role,
        content: m.text.trim(),
      }));

    setMessages((all) => [...all, { role: "user", text: trimmed, tools: [] }]);
    setQuestion("");
    setLoading(true);

    try {
      const response: ChatResponse = await askQuestion(trimmed, history);
      if (response.view && (response.tools?.length ?? 0) > 0) {
        onViewUpdate(response.view);
      }
      setMessages((all) => [
        ...all,
        {
          role: "assistant",
          text: messageText(response.answer, "No llegó una respuesta en texto."),
          tools: response.tools ?? [],
        },
      ]);
    } catch (error) {
      const textErr =
        error instanceof ApiError
          ? error.message
          : "No se pudo obtener una respuesta del servidor.";
      setMessages((all) => [
        ...all,
        { role: "assistant", text: textErr, tools: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function send(event: FormEvent) {
    event.preventDefault();
    sendText(question);
  }

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/90">
      <div className="shrink-0 border-b border-zinc-800 px-4 py-3">
        <p className="text-sm font-semibold text-zinc-100">Copiloto analítico</p>
        <p className="text-xs text-zinc-500">Respuestas ancladas a SQL y herramientas</p>
      </div>

      <div ref={listRef} className="min-h-0 flex-1 space-y-3 overflow-y-auto px-3 py-3">
        {messages.length === 0 ? (
          <div className="space-y-3 px-1">
            <p className="text-sm text-zinc-400">
              Preguntá sobre Nortec: ingresos, margen, regiones, canales o productos.
            </p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => sendText(s)}
                  className="rounded-full border border-zinc-700 bg-zinc-950 px-3 py-1.5 text-left text-xs text-zinc-300 transition hover:border-emerald-600/50 hover:text-zinc-100"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={cn(
                  "rounded-lg px-3 py-2 text-sm",
                  message.role === "user"
                    ? "ml-4 bg-emerald-950/50 text-zinc-100"
                    : "mr-2 bg-zinc-950 text-zinc-300",
                )}
              >
                <ChatBody
                  text={typeof message.text === "string" ? message.text : ""}
                />
                {message.role === "assistant" ? (
                  <ToolEvidence tools={message.tools} />
                ) : null}
              </div>
            ))}
          </>
        )}
        {loading ? (
          <p className="px-2 text-xs text-zinc-500" role="status">
            Consultando datos…
          </p>
        ) : null}
      </div>

      <form onSubmit={send} className="shrink-0 flex gap-2 border-t border-zinc-800 p-3">
        <input
          ref={inputRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Escribí tu pregunta…"
          className="min-w-0 flex-1 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-emerald-600 focus:outline-none"
          autoComplete="off"
          aria-label="Pregunta analítica"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-zinc-950 transition hover:bg-emerald-500 disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  );
}
