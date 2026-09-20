import type { CSSProperties } from "react";

export interface BarDatum {
  label: string;
  value: number;
  color: string;
}

interface MiniBarChartProps {
  items: BarDatum[];
}

export function MiniBarChart({ items }: MiniBarChartProps) {
  const max = Math.max(...items.map((i) => i.value), 1);

  return (
    <div className="mini-chart">
      <div className="bars">
        {items.map((item) => (
          <div
            key={item.label}
            className="bar-col"
            style={{ "--bar-color": item.color } as CSSProperties}
          >
            <div className="bar-value">{item.value}</div>
            <div
              className="bar"
              style={{ height: `${(item.value / max) * 100}%` }}
            />
            <div className="bar-label">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
