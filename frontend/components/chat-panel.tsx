"use client";

import { useState, type FormEvent } from "react";
import {
  askQuestion,
  type ChatResponse,
  type ToolResult,
} from "@/lib/api";
import { MiniBarChart, type BarDatum } from "@/components/mini-bar-chart";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  bars: BarDatum[] | null;
}

const PALETTE = [
  "#4f8cff",
  "#36d399",
  "#f4c95d",
  "#e879f9",
  "#ff7a59",
  "#5eead4",
];

function toolResultToBars(result: ToolResult): BarDatum[] | null {
  const data = result.result;
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return null;
  }
  const entries = Object.entries(data as Record<string, unknown>);
  const numeric = entries.filter(
    (entry): entry is [string, number] => typeof entry[1] === "number",
  );
  if (numeric.length === 0) {
    return null;
  }
  return numeric
    .sort((a, b) => b[1] - a[1])
    .map(([label, value], index) => ({
      label,
      value,
      color: PALETTE[index % PALETTE.length],
    }));
}

function answerToBars(response: ChatResponse): BarDatum[] | null {
  if (!response.tools || response.tools.length === 0) {
    return null;
  }
  for (const tool of response.tools) {
    const bars = toolResultToBars(tool);
    if (bars) {
      return bars;
    }
  }
  return null;
}

export function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  async function send(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) {
      return;
    }

    setMessages((all) => [...all, { role: "user", text: trimmed, bars: null }]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await askQuestion(trimmed);
      setMessages((all) => [
        ...all,
        {
          role: "assistant",
          text: response.answer,
          bars: answerToBars(response),
        },
      ]);
    } catch {
      setMessages((all) => [
        ...all,
        {
          role: "assistant",
          text: "No se pudo obtener una respuesta del servidor.",
          bars: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-placeholder">
            Preguntale sobre las ventas, por ejemplo: &quot;¿Cuál es la mejor categoría?&quot;
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`chat-message ${message.role}`}>
              <div className="chat-bubble">{message.text}</div>
              {message.bars ? <MiniBarChart items={message.bars} /> : null}
            </div>
          ))
        )}
      </div>
      <form className="chat-input-row" onSubmit={send}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Escribí tu pregunta sobre las ventas..."
          autoComplete="off"
        />
        <button type="submit" disabled={loading}>
          Enviar
        </button>
      </form>
    </div>
  );
}
