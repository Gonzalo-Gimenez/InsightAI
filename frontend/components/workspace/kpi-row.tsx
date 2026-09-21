import type { KpiBlock } from "@/lib/api";
import { formatCurrency, formatDelta, formatNumber } from "@/components/workspace/format";
import { cn } from "@/lib/cn";

const ITEMS = [
  { key: "ingresos" as const, label: "Ingresos", format: formatCurrency, deltaKey: "ingresos" },
  {
    key: "margen_pct" as const,
    label: "Margen %",
    format: (v: number | null) => (v == null ? "—" : `${v.toFixed(1)}%`),
    deltaKey: "margen",
  },
  { key: "ticket" as const, label: "Ticket prom.", format: formatCurrency, deltaKey: "ticket_promedio" },
  { key: "unidades" as const, label: "Unidades", format: formatNumber, deltaKey: "unidades" },
];

export function KpiRow({ kpis, loading }: { kpis: KpiBlock; loading?: boolean }) {
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {ITEMS.map((item) => {
        const raw = kpis[item.key];
        const delta = kpis.deltas?.[item.deltaKey];
        const deltaText = formatDelta(delta ?? null);
        const positive = delta != null && delta >= 0;
        return (
          <div
            key={item.key}
            className={cn(
              "rounded-xl border border-zinc-800 bg-zinc-900/80 px-4 py-3",
              loading && "animate-pulse",
            )}
          >
            <p className="text-[11px] font-medium uppercase tracking-wide text-zinc-400">
              {item.label}
            </p>
            <p className="mt-1 font-mono text-2xl font-medium tracking-tight text-zinc-50 tabular-nums">
              {loading ? "…" : item.format(raw ?? null)}
            </p>
            {deltaText ? (
              <p
                className={cn(
                  "mt-1 text-xs font-medium tabular-nums",
                  positive ? "text-emerald-400" : "text-rose-400",
                )}
              >
                {deltaText} vs período ant.
              </p>
            ) : (
              <p className="mt-1 text-xs text-zinc-600">vs período ant.</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
