"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError, getHealth, getMetrics, type WorkspaceView } from "@/lib/api";
import { ChartPanels } from "@/components/workspace/chart-panels";
import { CopilotPanel } from "@/components/workspace/copilot-panel";
import { KpiRow } from "@/components/workspace/kpi-row";
import { formatDay, formatPeriod } from "@/components/workspace/format";

const EMPTY_KPIS = {
  ingresos: null,
  margen_pct: null,
  ticket: null,
  unidades: null,
  deltas: null,
};

export function WorkspaceShell() {
  const [view, setView] = useState<WorkspaceView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dbStatus, setDbStatus] = useState<"ok" | "degraded" | "unknown">("unknown");

  const loadMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [health, metrics] = await Promise.all([getHealth(), getMetrics()]);
      setDbStatus(
        health.status === "ok" && health.database === "up" ? "ok" : "degraded",
      );
      if (metrics.view) {
        setView(metrics.view);
        if (health.status !== "ok") {
          setDbStatus("ok");
        }
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al cargar el workspace.");
      setView({
        period: {},
        kpis: EMPTY_KPIS,
        charts: [],
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMetrics();
  }, [loadMetrics]);

  const onViewUpdate = useCallback((next: WorkspaceView) => {
    setView((prev) => ({
      ...next,
      coverage: next.coverage ?? prev?.coverage ?? null,
      charts:
        next.charts && next.charts.length > 0 ? next.charts : (prev?.charts ?? []),
    }));
  }, []);

  const kpis = view?.kpis ?? EMPTY_KPIS;
  const charts = view?.charts ?? [];
  const fromQuery = view?.source === "query";
  const periodLabel = formatPeriod(view?.period?.from, view?.period?.to);
  const coverageFrom = formatDay(view?.coverage?.from);
  const coverageTo = formatDay(view?.coverage?.to);

  return (
    <div className="flex h-dvh min-h-0 flex-col overflow-hidden bg-zinc-950 text-zinc-100">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 px-4 py-3 lg:px-6">
        <div>
          <p className="text-lg font-semibold tracking-tight">
            Nortec <span className="text-zinc-500 font-normal">· InsightAI</span>
          </p>
          <p className="text-xs text-zinc-500">Workspace de BI conversacional</p>
        </div>
        <div className="flex flex-col items-end gap-0.5 text-xs text-zinc-400">
          <div className="flex items-center gap-3">
            {fromQuery ? (
              <button
                type="button"
                onClick={loadMetrics}
                className="rounded-md border border-zinc-700 px-2.5 py-1 text-xs text-zinc-300 transition hover:border-emerald-600/60 hover:text-zinc-50"
              >
                Vista inicial
              </button>
            ) : null}
            <span>
              <span className="text-zinc-500">Ventana </span>
              <span className="font-mono tabular-nums">{periodLabel}</span>
            </span>
            <span
              className={
                dbStatus === "ok"
                  ? "text-emerald-400"
                  : dbStatus === "degraded"
                    ? "text-amber-400"
                    : "text-zinc-500"
              }
            >
              {dbStatus === "ok"
                ? "DB conectada"
                : dbStatus === "unknown"
                  ? "DB…"
                  : "DB degradada"}
            </span>
          </div>
          {coverageFrom && coverageTo ? (
            <span className="text-zinc-600">
              Datos disponibles {coverageFrom} a {coverageTo}
            </span>
          ) : null}
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden p-4 lg:flex-row lg:gap-5 lg:p-6">
        <main className="flex min-h-0 min-w-0 flex-1 flex-col gap-4 overflow-y-auto lg:overflow-hidden">
          {error ? (
            <div
              className="shrink-0 rounded-lg border border-amber-900/50 bg-amber-950/30 px-4 py-3 text-sm text-amber-100"
              role="alert"
            >
              {error}
              <button
                type="button"
                onClick={loadMetrics}
                className="ml-3 underline hover:no-underline"
              >
                Reintentar
              </button>
            </div>
          ) : null}
          <div className="shrink-0">
            <KpiRow kpis={kpis} loading={loading} />
          </div>
          <div className="min-h-0 flex-1">
            <ChartPanels charts={charts} />
          </div>
        </main>

        <aside className="flex h-[min(52dvh,520px)] w-full shrink-0 flex-col lg:h-auto lg:min-h-0 lg:w-[min(400px,38vw)] lg:self-stretch">
          <div className="min-h-0 flex-1">
            <CopilotPanel onViewUpdate={onViewUpdate} />
          </div>
        </aside>
      </div>
    </div>
  );
}
