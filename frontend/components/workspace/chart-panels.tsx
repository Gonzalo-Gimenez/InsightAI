"use client";

import type { ReactNode } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartSpec } from "@/lib/api";
import { formatCurrency } from "@/components/workspace/format";

const PIE_COLORS = ["#34d399", "#38bdf8", "#fbbf24", "#a1a1aa", "#fb7185"];

function ChartBody({ children }: { children: ReactNode }) {
  return <div className="h-full min-h-[12rem] w-full">{children}</div>;
}

function LinePanel({ chart }: { chart: ChartSpec }) {
  const data = (chart.data as { label?: string; valor?: number }[]).map((d) => ({
    name: d.label ?? "",
    valor: d.valor ?? 0,
  }));
  return (
    <ChartBody>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#27272a" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: "#a1a1aa", fontSize: 11 }} tickLine={false} />
          <YAxis
            tick={{ fill: "#a1a1aa", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `${Math.round(v / 1000)}k`}
          />
          <Tooltip
            contentStyle={{
              background: "#18181b",
              border: "1px solid #3f3f46",
              borderRadius: 8,
            }}
            formatter={(value) => [
              formatCurrency(typeof value === "number" ? value : Number(value)),
              "Ingresos",
            ]}
          />
          <Line
            type="monotone"
            dataKey="valor"
            stroke="#34d399"
            strokeWidth={2}
            dot={data.length < 2}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartBody>
  );
}

function BarPanel({ chart }: { chart: ChartSpec }) {
  const data = (chart.data as { label?: string; value?: number; clave?: string; ingresos?: number }[]).map(
    (d) => ({
      name: d.label ?? d.clave ?? "",
      value: d.value ?? (d.ingresos != null ? Number(d.ingresos) : 0),
    }),
  );
  return (
    <ChartBody>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#27272a" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: "#a1a1aa", fontSize: 10 }} tickLine={false} />
          <YAxis
            tick={{ fill: "#a1a1aa", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `${Math.round(v / 1000)}k`}
          />
          <Tooltip
            contentStyle={{
              background: "#18181b",
              border: "1px solid #3f3f46",
              borderRadius: 8,
            }}
            formatter={(value) => [
              formatCurrency(typeof value === "number" ? value : Number(value)),
              "Ingresos",
            ]}
          />
          <Bar dataKey="value" fill="#34d399" radius={[4, 4, 0, 0]} maxBarSize={40} />
        </BarChart>
      </ResponsiveContainer>
    </ChartBody>
  );
}

function PiePanel({ chart }: { chart: ChartSpec }) {
  const data = (
    chart.data as { label?: string; value?: number; clave?: string; ingresos?: number }[]
  ).map((d) => ({
    name: d.label ?? d.clave ?? "",
    value: d.value ?? (d.ingresos != null ? Number(d.ingresos) : 0),
  }));
  const total = data.reduce((sum, d) => sum + d.value, 0);

  return (
    <ChartBody>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="46%"
            innerRadius={48}
            outerRadius={78}
            paddingAngle={2}
            stroke="#18181b"
          >
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#18181b",
              border: "1px solid #3f3f46",
              borderRadius: 8,
            }}
            formatter={(value, name) => {
              const amount = typeof value === "number" ? value : Number(value);
              const pct = total ? ` (${((amount / total) * 100).toFixed(1)}%)` : "";
              return [formatCurrency(amount) + pct, String(name)];
            }}
          />
          <Legend
            verticalAlign="bottom"
            formatter={(value) => <span className="text-xs text-zinc-400">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartBody>
  );
}

function TablePanel({ chart }: { chart: ChartSpec }) {
  const rows = chart.data as Record<string, unknown>[];
  if (!rows.length) {
    return <p className="text-sm text-zinc-500">Sin filas.</p>;
  }
  const cols = Object.keys(rows[0]).slice(0, 6);
  return (
    <div className="h-full min-h-0 overflow-auto">
      <table className="w-full text-left text-sm">
        <thead className="sticky top-0 bg-zinc-900">
          <tr className="border-b border-zinc-800 text-zinc-500">
            {cols.map((c) => (
              <th key={c} className="pb-2 pr-3 font-medium">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className={
                i % 2 === 0
                  ? "border-b border-zinc-800/60 bg-zinc-900/40"
                  : "border-b border-zinc-800/60"
              }
            >
              {cols.map((c) => (
                <td key={c} className="py-2 pr-3 font-mono text-xs text-zinc-300">
                  {String(row[c] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function barValues(chart: ChartSpec): number[] {
  return (chart.data as { value?: number; ingresos?: number }[]).map((row) =>
    Number(row.value ?? row.ingresos ?? 0),
  );
}

export function ChartPanels({ charts }: { charts: ChartSpec[] }) {
  const usable = charts
    .filter((chart) => Array.isArray(chart.data) && chart.data.length > 0)
    .filter((chart) => chart.type !== "bar" || barValues(chart).some((value) => value !== 0))
    .slice(0, 4);
  if (!usable.length) {
    return (
      <div className="flex h-full min-h-[12rem] items-center justify-center rounded-xl border border-dashed border-zinc-700 bg-zinc-900/40 px-6 py-12 text-center text-sm text-zinc-500">
        Hacé una pregunta en el copiloto para actualizar gráficos y tablas.
      </div>
    );
  }

  return (
    <div className="grid h-full min-h-[36rem] grid-cols-1 gap-4 lg:min-h-0 lg:grid-cols-2 lg:grid-rows-2">
      {usable.map((chart) => (
        <div
          key={chart.id}
          className="flex min-h-0 flex-col rounded-xl border border-zinc-800 bg-zinc-900/60 p-4"
        >
          <h3 className="mb-3 shrink-0 text-sm font-medium text-zinc-200">{chart.title}</h3>
          <div className="min-h-0 flex-1">
            {chart.type === "line" ? <LinePanel chart={chart} /> : null}
            {chart.type === "bar" ? <BarPanel chart={chart} /> : null}
            {chart.type === "pie" ? <PiePanel chart={chart} /> : null}
            {chart.type === "table" ? <TablePanel chart={chart} /> : null}
          </div>
        </div>
      ))}
    </div>
  );
}
