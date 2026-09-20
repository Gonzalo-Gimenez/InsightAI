import { ChatPanel } from "@/components/chat-panel";
import { HeroHeader } from "@/components/hero-header";
import { MetricsViz } from "@/components/metrics-viz";

export default function HomePage() {
  return (
    <main className="shell">
      <HeroHeader />
      <MetricsViz />
      <aside className="chat-aside">
        <div className="chat-title">
          <span className="chat-dot" aria-hidden />
          Asistente de ventas
        </div>
        <ChatPanel />
      </aside>
    </main>
  );
}
