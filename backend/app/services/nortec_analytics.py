"""Consultas agregadas sobre el warehouse Nortec (solo SQL, sin cargar el fact en memoria)."""

from datetime import date, timedelta
from typing import Any

from app.services.ventas_db import run_parameterized_select, run_scalar_query


def _parse_date(value: str | None, default: date) -> date:
    if not value:
        return default
    return date.fromisoformat(value)


def date_bounds() -> tuple[date, date]:
    row = run_scalar_query(
        "SELECT MIN(fecha)::text, MAX(fecha)::text FROM fact_ventas"
    )
    if not row or not row[0]:
        raise ValueError("fact_ventas vacía")
    return date.fromisoformat(row[0]), date.fromisoformat(row[1])


def default_period() -> tuple[date, date]:
    min_d, max_d = date_bounds()
    return months_back(max_d, 12, min_d), max_d


def months_back(hasta: date, meses: int, min_d: date) -> date:
    """Primer día del mes, N meses hacia atrás incluyendo el mes de hasta."""
    n = max(1, min(int(meses), 24))
    year, month = hasta.year, hasta.month - (n - 1)
    while month <= 0:
        month += 12
        year -= 1
    return max(min_d, date(year, month, 1))


def series_window(desde: date, hasta: date, min_d: date) -> tuple[date, date]:
    """Una serie mensual de un solo mes no dibuja línea: abrir a 12 meses."""
    months = (hasta.year - desde.year) * 12 + (hasta.month - desde.month)
    if months < 1:
        desde = months_back(hasta, 12, min_d)
        return desde, hasta
    return max(desde, min_d), hasta


def _line_metrics(
    fecha_desde: date,
    fecha_hasta: date,
    extra_where: str = "",
    params: tuple = (),
) -> dict[str, Any]:
    sql = f"""
        SELECT
            COALESCE(SUM(ingresos), 0) AS ingresos,
            COALESCE(SUM(margen), 0) AS margen,
            COALESCE(SUM(cantidad), 0) AS unidades,
            COUNT(DISTINCT linea_id) AS tickets
        FROM v_ventas_linea
        WHERE fecha >= %s AND fecha <= %s
        {extra_where}
    """
    row = run_scalar_query(sql, (fecha_desde, fecha_hasta, *params))
    ingresos = float(row[0] or 0)
    margen = float(row[1] or 0)
    unidades = int(row[2] or 0)
    tickets = int(row[3] or 0)
    ticket_promedio = ingresos / tickets if tickets else 0.0
    margen_pct = (margen / ingresos * 100.0) if ingresos else 0.0
    return {
        "ingresos": round(ingresos, 2),
        "margen": round(margen, 2),
        "margen_pct": round(margen_pct, 2),
        "unidades": unidades,
        "tickets": tickets,
        "ticket_promedio": round(ticket_promedio, 2),
    }


def _filter_sucursal(sucursal: str | None) -> tuple[str, list[Any]]:
    if sucursal and str(sucursal).strip():
        return " AND sucursal ILIKE %s", [str(sucursal).strip()]
    return "", []


def _year_bounds(anio: Any) -> tuple[date, date] | None:
    if anio is None:
        return None
    try:
        year = int(anio)
    except (TypeError, ValueError):
        return None
    return date(year, 1, 1), date(year, 12, 31)


def kpis_periodo(
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    region: str | None = None,
    categoria: str | None = None,
    canal: str | None = None,
    sucursal: str | None = None,
    anio: int | None = None,
) -> dict[str, Any]:
    d_start_default, d_end_default = default_period()
    year = _year_bounds(anio)
    if year:
        desde, hasta = year
    else:
        desde = _parse_date(fecha_desde, d_start_default)
        hasta = _parse_date(fecha_hasta, d_end_default)

    clauses = []
    params: list[Any] = []
    if region:
        clauses.append("AND region = %s")
        params.append(region)
    if categoria:
        clauses.append("AND categoria = %s")
        params.append(categoria)
    if canal:
        clauses.append("AND canal = %s")
        params.append(canal)
    extra_suc, suc_params = _filter_sucursal(sucursal)
    extra = " ".join(clauses) + extra_suc
    params.extend(suc_params)

    current = _line_metrics(desde, hasta, extra, tuple(params))
    span = (hasta - desde).days + 1
    prev_hasta = desde - timedelta(days=1)
    prev_desde = prev_hasta - timedelta(days=span - 1)
    previous = _line_metrics(prev_desde, prev_hasta, extra, tuple(params))

    def delta(cur: float, prev: float) -> float | None:
        if prev == 0:
            return None
        return round((cur - prev) / prev * 100.0, 2)

    return {
        "periodo": {"desde": desde.isoformat(), "hasta": hasta.isoformat()},
        "kpis": current,
        "periodo_anterior": {
            "desde": prev_desde.isoformat(),
            "hasta": prev_hasta.isoformat(),
        },
        "deltas_pct": {
            "ingresos": delta(current["ingresos"], previous["ingresos"]),
            "margen": delta(current["margen"], previous["margen"]),
            "unidades": delta(float(current["unidades"]), float(previous["unidades"])),
            "ticket_promedio": delta(
                current["ticket_promedio"], previous["ticket_promedio"]
            ),
        },
        "sql": (
            "SELECT SUM(ingresos), SUM(margen), SUM(cantidad), COUNT(DISTINCT linea_id) "
            f"FROM v_ventas_linea WHERE fecha BETWEEN '{desde}' AND '{hasta}' {extra}"
        ),
        "sucursal": sucursal,
    }


def serie_mensual(
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    metrica: str = "ingresos",
    meses: int | None = None,
    sucursal: str | None = None,
    anio: int | None = None,
) -> dict[str, Any]:
    desde_def, hasta_def = default_period()
    min_d, max_d = date_bounds()
    year = _year_bounds(anio)
    if year:
        desde, hasta = max(year[0], min_d), min(year[1], max_d)
    else:
        hasta = min(_parse_date(fecha_hasta, hasta_def), max_d)
        if meses is not None:
            desde = months_back(hasta, meses, min_d)
        else:
            desde = _parse_date(fecha_desde, desde_def)
            desde, hasta = series_window(desde, hasta, min_d)
    col = "ingresos" if metrica != "margen" else "margen"
    extra, extra_params = _filter_sucursal(sucursal)
    sql = f"""
        SELECT anio, mes, ROUND(SUM({col})::numeric, 2) AS valor
        FROM v_ventas_linea
        WHERE fecha >= %s AND fecha <= %s
        {extra}
        GROUP BY anio, mes
        ORDER BY anio, mes
        LIMIT 100
    """
    rows = run_parameterized_select(sql, (desde, hasta, *extra_params))
    series = [
        {
            "label": f"{int(r['anio'])}-{int(r['mes']):02d}",
            "anio": int(r["anio"]),
            "mes": int(r["mes"]),
            "valor": float(r["valor"]),
        }
        for r in rows
    ]
    return {
        "metrica": col,
        "serie": series,
        "sql": sql.strip(),
        "periodo": {"desde": desde.isoformat(), "hasta": hasta.isoformat()},
        "sucursal": sucursal,
    }

def ranking_productos(
    limite: int = 10,
    orden: str = "ingresos",
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    region: str | None = None,
    sucursal: str | None = None,
    anio: int | None = None,
) -> dict[str, Any]:
    desde_def, hasta_def = default_period()
    year = _year_bounds(anio)
    if year:
        desde, hasta = year
    else:
        desde = _parse_date(fecha_desde, desde_def)
        hasta = _parse_date(fecha_hasta, hasta_def)
    limite = max(1, min(int(limite), 50))
    col = "ingresos" if orden != "margen" else "margen"
    extra = ""
    params: list[Any] = [desde, hasta]
    if region:
        extra += " AND region = %s"
        params.append(region)
    suc_sql, suc_params = _filter_sucursal(sucursal)
    extra += suc_sql
    params.extend(suc_params)
    params.append(limite)
    sql = f"""
        SELECT producto, sku, categoria,
               ROUND(SUM(ingresos)::numeric, 2) AS ingresos,
               ROUND(SUM(margen)::numeric, 2) AS margen
        FROM v_ventas_linea
        WHERE fecha >= %s AND fecha <= %s
        {extra}
        GROUP BY producto, sku, categoria
        ORDER BY {col} DESC
        LIMIT %s
    """
    rows = run_parameterized_select(sql, tuple(params))
    return {
        "orden": col,
        "limite": limite,
        "productos": rows,
        "sql": sql.strip(),
        "region": region,
        "sucursal": sucursal,
        "periodo": {"desde": desde.isoformat(), "hasta": hasta.isoformat()},
    }


def mix_dimension(
    dimension: str,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    limite: int | None = None,
    sucursal: str | None = None,
    anio: int | None = None,
) -> dict[str, Any]:
    allowed = {"categoria": "categoria", "region": "region", "canal": "canal"}
    if dimension not in allowed:
        raise ValueError(f"Dimensión no válida: {dimension}")
    col = allowed[dimension]
    desde_def, hasta_def = default_period()
    year = _year_bounds(anio)
    if year:
        desde, hasta = year
    else:
        desde = _parse_date(fecha_desde, desde_def)
        hasta = _parse_date(fecha_hasta, hasta_def)
    cap = max(1, min(int(limite), 20)) if limite else 100
    extra, extra_params = _filter_sucursal(sucursal)
    sql = f"""
        SELECT {col} AS clave,
               ROUND(SUM(ingresos)::numeric, 2) AS ingresos,
               ROUND(SUM(margen)::numeric, 2) AS margen
        FROM v_ventas_linea
        WHERE fecha >= %s AND fecha <= %s
        {extra}
        GROUP BY {col}
        ORDER BY ingresos DESC
        LIMIT %s
    """
    rows = run_parameterized_select(sql, (desde, hasta, *extra_params, cap))
    return {
        "dimension": dimension,
        "mix": rows,
        "sql": sql.strip(),
        "limite": limite,
        "sucursal": sucursal,
        "periodo": {"desde": desde.isoformat(), "hasta": hasta.isoformat()},
    }


def ticket_promedio_por(
    agrupar: str = "region",
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> dict[str, Any]:
    allowed = {"region": "region", "segmento": "segmento", "sucursal": "sucursal"}
    if agrupar not in allowed:
        raise ValueError(f"Agrupación no válida: {agrupar}")
    col = allowed[agrupar]
    desde_def, hasta_def = default_period()
    desde = _parse_date(fecha_desde, desde_def)
    hasta = _parse_date(fecha_hasta, hasta_def)
    sql = f"""
        SELECT {col} AS clave,
               ROUND(SUM(ingresos)::numeric, 2) AS ingresos,
               COUNT(DISTINCT linea_id) AS tickets,
               ROUND(
                   (SUM(ingresos) / NULLIF(COUNT(DISTINCT linea_id), 0))::numeric,
                   2
               ) AS ticket_promedio
        FROM v_ventas_linea
        WHERE fecha >= %s AND fecha <= %s
        GROUP BY {col}
        ORDER BY ticket_promedio DESC
        LIMIT 100
    """
    rows = run_parameterized_select(sql, (desde, hasta))
    return {"agrupar": agrupar, "filas": rows, "sql": sql.strip()}


def comparar_periodos(
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> dict[str, Any]:
    actual = kpis_periodo(fecha_desde, fecha_hasta)
    return {
        "actual": actual["kpis"],
        "deltas_pct": actual["deltas_pct"],
        "periodo": actual["periodo"],
        "periodo_anterior": actual["periodo_anterior"],
    }


def listar_esquema() -> dict[str, Any]:
    return {
        "tablas": [
            "dim_tiempo",
            "dim_producto",
            "dim_cliente",
            "dim_sucursal",
            "fact_ventas",
            "v_ventas_linea (vista)",
        ],
        "vista_principal": "v_ventas_linea",
        "columnas_vista": [
            "fecha",
            "mes",
            "trimestre",
            "anio",
            "producto",
            "sku",
            "categoria",
            "subcategoria",
            "marca",
            "segmento",
            "region",
            "canal",
            "sucursal",
            "cantidad",
            "ingresos",
            "margen",
        ],
    }


def describir_tabla(tabla: str) -> dict[str, Any]:
    allowed = {
        "dim_tiempo",
        "dim_producto",
        "dim_cliente",
        "dim_sucursal",
        "fact_ventas",
        "v_ventas_linea",
    }
    if tabla not in allowed:
        raise ValueError(f"Tabla no permitida: {tabla}")
    if tabla == "v_ventas_linea":
        return listar_esquema()
    rows = run_parameterized_select(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        LIMIT 100
        """,
        (tabla,),
    )
    return {"tabla": tabla, "columnas": rows}


def _chart_scope_suffix(*payloads: dict | None) -> str:
    sucursal = None
    periodo = None
    for payload in payloads:
        if not payload:
            continue
        sucursal = payload.get("sucursal") or sucursal
        periodo = payload.get("periodo") or periodo
    bits: list[str] = []
    if sucursal:
        bits.append(str(sucursal))
    if periodo and periodo.get("desde") and periodo.get("hasta"):
        start, end = str(periodo["desde"]), str(periodo["hasta"])
        if start[:4] == end[:4]:
            bits.append(start[:4])
    return (" · " + " · ".join(bits)) if bits else ""


def build_view_from_payloads(
    kpi_payload: dict,
    serie_payload: dict | None = None,
    mix_payload: dict | None = None,
    ranking_payload: dict | None = None,
    pie_payload: dict | None = None,
) -> dict[str, Any]:
    period = kpi_payload.get("periodo", {})
    kpis = kpi_payload.get("kpis", {})
    deltas = kpi_payload.get("deltas_pct", {})
    charts: list[dict[str, Any]] = []
    try:
        min_d, max_d = date_bounds()
        coverage = {"from": min_d.isoformat(), "to": max_d.isoformat()}
    except Exception:
        coverage = {}

    suffix = _chart_scope_suffix(
        kpi_payload, serie_payload, mix_payload, ranking_payload, pie_payload
    )

    if serie_payload and serie_payload.get("serie"):
        n = len(serie_payload["serie"])
        charts.append(
            {
                "id": "serie_mensual",
                "type": "line",
                "title": (f"Ingresos por mes · {n} meses" if n else "Ingresos por mes")
                + suffix,
                "data": serie_payload["serie"],
            }
        )
    if mix_payload and mix_payload.get("mix"):
        dim = mix_payload.get("dimension") or "categoría"
        title = f"Mix por {dim}"
        if mix_payload.get("limite"):
            title = f"{title} · top {int(mix_payload['limite'])}"
        charts.append(
            {
                "id": f"mix_{dim}",
                "type": "bar",
                "title": title + suffix,
                "data": [
                    {"label": r["clave"], "value": float(r["ingresos"])}
                    for r in mix_payload["mix"]
                ],
            }
        )
    if pie_payload and pie_payload.get("mix"):
        charts.append(
            {
                "id": "mix_canal",
                "type": "pie",
                "title": "Mix por canal" + suffix,
                "data": [
                    {"label": r["clave"], "value": float(r["ingresos"])}
                    for r in pie_payload["mix"]
                ],
            }
        )
    if ranking_payload and ranking_payload.get("productos"):
        cap = int(ranking_payload.get("limite") or 8)
        charts.append(
            {
                "id": "ranking_productos",
                "type": "table",
                "title": f"Top {cap} productos" + suffix,
                "data": ranking_payload["productos"][:cap],
            }
        )

    return {
        "period": {
            "from": period.get("desde"),
            "to": period.get("hasta"),
        },
        "coverage": coverage,
        "kpis": {
            "ingresos": kpis.get("ingresos"),
            "margen_pct": kpis.get("margen_pct"),
            "ticket": kpis.get("ticket_promedio"),
            "unidades": kpis.get("unidades"),
            "deltas": deltas,
        },
        "charts": charts,
        "source": "default",
    }


def charts_for_period(
    fecha_desde: str,
    fecha_hasta: str,
    sucursal: str | None = None,
    anio: int | None = None,
) -> tuple:
    return (
        serie_mensual(
            fecha_desde, fecha_hasta, sucursal=sucursal, anio=anio
        ),
        mix_dimension(
            "categoria", fecha_desde, fecha_hasta, sucursal=sucursal, anio=anio
        ),
        ranking_productos(
            8, "ingresos", fecha_desde, fecha_hasta, sucursal=sucursal, anio=anio
        ),
        mix_dimension(
            "canal", fecha_desde, fecha_hasta, sucursal=sucursal, anio=anio
        ),
    )


def workspace_default_view() -> dict[str, Any]:
    period = default_period()
    desde = period[0].isoformat()
    hasta = period[1].isoformat()
    kpi_payload = kpis_periodo(fecha_desde=desde, fecha_hasta=hasta)
    serie, mix, ranking, pie = charts_for_period(desde, hasta)
    return build_view_from_payloads(kpi_payload, serie, mix, ranking, pie)
