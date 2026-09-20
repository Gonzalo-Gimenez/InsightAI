"use client";

import { useEffect, useState, type CSSProperties } from "react";
import { Chart3d } from "@/components/chart3d";
import { getMetrics, type MetricsResponse } from "@/lib/api";

const API_ERROR =
  "No se pudo conectar con la API. Asegurate de que el backend esté corriendo en http://127.0.0.1:8000";

export function MetricsViz() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getMetrics()
      .then((data) => {
        if (!cancelled) {
          setMetrics(data);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(API_ERROR);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="viz-section">
      {error ? (
        <div className="error-banner">{error}</div>
      ) : !metrics ? (
        <div className="loading-banner">Cargando métricas…</div>
      ) : (
        <>
          <div className="kpis">
            <div className="kpi" style={{ "--kpi-color": "#4f8cff" } as CSSProperties}>
              <span className="kpi-icon">Σ</span>
              <div className="kpi-text">
                <span className="kpi-label">Total</span>
                <span className="kpi-value">{metrics.total_ventas}</span>
              </div>
            </div>
            <div className="kpi" style={{ "--kpi-color": "#36d399" } as CSSProperties}>
              <span className="kpi-icon">x̄</span>
              <div className="kpi-text">
                <span className="kpi-label">Promedio</span>
                <span className="kpi-value">{metrics.promedio_ventas}</span>
              </div>
            </div>
            <div className="kpi" style={{ "--kpi-color": "#f4c95d" } as CSSProperties}>
              <span className="kpi-icon">▲</span>
              <div className="kpi-text">
                <span className="kpi-label">Máxima</span>
                <span className="kpi-value">{metrics.venta_maxima.producto}</span>
                <span className="kpi-sub">{metrics.venta_maxima.ventas} ventas</span>
              </div>
            </div>
            <div className="kpi" style={{ "--kpi-color": "#e879f9" } as CSSProperties}>
              <span className="kpi-icon">▼</span>
              <div className="kpi-text">
                <span className="kpi-label">Mínima</span>
                <span className="kpi-value">{metrics.venta_minima.producto}</span>
                <span className="kpi-sub">{metrics.venta_minima.ventas} ventas</span>
              </div>
            </div>
          </div>
          <div className="chart3d-wrap">
            <Chart3d metrics={metrics} />
          </div>
        </>
      )}
    </section>
  );
}
