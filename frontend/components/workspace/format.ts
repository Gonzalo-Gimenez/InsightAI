export function formatCurrency(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) {
    return "—";
  }
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) {
    return "—";
  }
  return new Intl.NumberFormat("es-AR").format(value);
}

export function formatDelta(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) {
    return "";
  }
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}%`;
}

export function formatPeriod(from?: string | null, to?: string | null): string {
  if (!from || !to) {
    return "Últimos 30 días";
  }
  return `${from} → ${to}`;
}

export function formatDay(iso?: string | null): string {
  if (!iso) return "";
  const [year, month, day] = iso.split("-");
  if (!year || !month || !day) return iso;
  return `${day}/${month}/${year}`;
}
