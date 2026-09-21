"""Construye ViewSpec para el canvas a partir de herramientas ejecutadas."""

import re
from decimal import Decimal
from typing import Any

from app.services import nortec_analytics as na

_MAX_CHARTS = 4
_IDISH = {"id", "linea_id", "producto_id", "cliente_id", "sucursal_id"}
_BRANCH_NAMES = (
    "Centro Córdoba",
    "Rosario Norte",
    "Mendoza Plaza",
    "Salta Centro",
    "Palermo",
    "Belgrano",
    "La Plata",
    "Neuquén",
    "Tucumán",
    "Mar del Plata",
    "Tienda Online AR",
    "Outlet Online",
)


def _num(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_idish(key: str) -> bool:
    lowered = key.lower()
    return lowered in _IDISH or lowered.endswith("_id")


def _charts_from_sql_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows or not isinstance(rows[0], dict):
        return []

    table = {
        "id": "sql_table",
        "type": "table",
        "title": f"Resultado ({len(rows)})",
        "data": rows[:100],
    }
    keys = list(rows[0].keys())
    metric_keys = [
        key
        for key in keys
        if _num(rows[0].get(key)) is not None and not _is_idish(key)
    ]
    # Un COUNT / un solo número vive en el chat, no ocupa un tile.
    if len(rows) < 2:
        return []
    # Catálogo (id + nombre): tabla, no un eje de IDs.
    if not metric_keys:
        return [table]

    label_key = next((key for key in keys if key not in metric_keys), keys[0])
    value_key = metric_keys[0]
    return [
        {
            "id": "sql_result",
            "type": "bar",
            "title": "Resultado de consulta",
            "data": [
                {
                    "label": str(row.get(label_key)),
                    "value": _num(row.get(value_key)) or 0,
                }
                for row in rows[:20]
            ],
        },
        table,
    ]


def _prioritize_charts(
    charts: list[dict[str, Any]], priority_ids: list[str]
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    head: list[dict[str, Any]] = []
    by_id = {chart["id"]: chart for chart in charts}
    for chart_id in priority_ids:
        chart = by_id.get(chart_id)
        if chart and chart_id not in seen:
            head.append(chart)
            seen.add(chart_id)
    tail = [chart for chart in charts if chart["id"] not in seen]
    return (head + tail)[:_MAX_CHARTS]


def _priority_ids(tools: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for tool in tools:
        if not isinstance(tool.get("result"), dict) or tool["result"].get("error"):
            continue
        name = tool.get("name")
        if name == "serie_mensual":
            ids.append("serie_mensual")
        elif name in ("mix_categoria", "mix_region"):
            dim = tool["result"].get("dimension") or name.replace("mix_", "")
            ids.append(f"mix_{dim}")
        elif name == "mix_canal":
            ids.append("mix_canal")
        elif name == "ranking_productos":
            ids.append("ranking_productos")
        elif name == "ticket_promedio":
            ids.append("ticket_promedio")
        elif name == "consultar_sql":
            ids.extend(["sql_result", "sql_table"])
    return ids


def _sucursal_from_sql(sql: str) -> str | None:
    match = re.search(
        r"(?:[\w.]*)sucursal\s*(?:=|ILIKE|LIKE)\s*'%?([^'%]+)%?'",
        sql,
        re.I,
    )
    if match:
        return match.group(1).strip()
    match = re.search(r"(?:[\w.]*)sucursal\s+IN\s*\(\s*'([^']+)'", sql, re.I)
    if match:
        return match.group(1).strip()
    lowered = sql.lower()
    for name in sorted(_BRANCH_NAMES, key=len, reverse=True):
        if f"'{name.lower()}'" in lowered:
            return name
    return None


def _year_from_sql(sql: str) -> int | None:
    match = re.search(
        r"(?:EXTRACT\s*\(\s*YEAR\s+FROM\s+[^)]+\)|"
        r"DATE_PART\s*\(\s*'year'\s*,\s*[^)]+\))\s*=\s*'?(\d{4})'?",
        sql,
        re.I,
    )
    if match:
        return int(match.group(1))
    match = re.search(r"\banio\s*=\s*'?(\d{4})'?", sql, re.I)
    if match:
        return int(match.group(1))
    return None


def _infer_scope(tools: list[dict[str, Any]]) -> dict[str, Any]:
    sucursal = None
    anio = None
    desde = None
    hasta = None
    for tool in tools:
        args = tool.get("arguments") or {}
        result = tool.get("result") if isinstance(tool.get("result"), dict) else {}
        if args.get("sucursal"):
            sucursal = str(args["sucursal"]).strip()
        elif result.get("sucursal"):
            sucursal = str(result["sucursal"]).strip()
        for raw in (args.get("anio"), result.get("anio")):
            if raw is None:
                continue
            try:
                anio = int(raw)
                break
            except (TypeError, ValueError):
                pass
        periodo = result.get("periodo") if isinstance(result, dict) else None
        if isinstance(periodo, dict):
            desde = periodo.get("desde") or desde
            hasta = periodo.get("hasta") or hasta
        sql = f"{result.get('sql') or ''} {args.get('sql') or ''}"
        sucursal = _sucursal_from_sql(sql) or sucursal
        year_from_sql = _year_from_sql(sql)
        if year_from_sql:
            anio = year_from_sql
        match = re.search(
            r"BETWEEN\s+'(\d{4}-\d{2}-\d{2})'\s+AND\s+'(\d{4}-\d{2}-\d{2})'",
            sql,
            re.I,
        )
        if match:
            desde, hasta = match.group(1), match.group(2)
        match = re.search(r"fecha\s*>=\s*'(\d{4}-\d{2}-\d{2})'", sql, re.I)
        if match:
            desde = match.group(1)
        match = re.search(r"fecha\s*<=\s*'(\d{4}-\d{2}-\d{2})'", sql, re.I)
        if match:
            hasta = match.group(1)
    if anio and not desde:
        desde = f"{anio}-01-01"
        hasta = f"{anio}-12-31"
    elif desde and hasta and not anio and str(desde)[:4] == str(hasta)[:4]:
        anio = int(str(desde)[:4])
    return {"sucursal": sucursal, "anio": anio, "desde": desde, "hasta": hasta}


def infer_view_from_tools(tools: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not tools:
        return None

    kpi_payload = None
    serie_payload = None
    mix_payload = None
    ranking_payload = None
    pie_payload = None
    extra_charts: list[dict[str, Any]] = []

    for tool in tools:
        name = tool.get("name")
        result = tool.get("result")
        if not isinstance(result, dict) or result.get("error"):
            continue
        if name == "kpis_periodo":
            kpi_payload = result
        elif name == "serie_mensual":
            serie_payload = result
        elif name in ("mix_categoria", "mix_region"):
            mix_payload = {
                "mix": [
                    {"clave": r.get("clave"), "ingresos": r.get("ingresos")}
                    for r in result.get("mix", [])
                ],
                "dimension": result.get("dimension") or name.replace("mix_", ""),
                "limite": result.get("limite"),
                "sucursal": result.get("sucursal"),
                "periodo": result.get("periodo"),
            }
        elif name == "mix_canal":
            pie_payload = {
                "mix": [
                    {"clave": r.get("clave"), "ingresos": r.get("ingresos")}
                    for r in result.get("mix", [])
                ],
                "sucursal": result.get("sucursal"),
                "periodo": result.get("periodo"),
            }
        elif name == "ranking_productos":
            ranking_payload = result
        elif name == "comparar_periodos" and "actual" in result:
            kpi_payload = {
                "periodo": result.get("periodo", {}),
                "kpis": result.get("actual", {}),
                "deltas_pct": result.get("deltas_pct", {}),
            }
        elif name == "ticket_promedio" and result.get("filas"):
            extra_charts.append(
                {
                    "id": "ticket_promedio",
                    "type": "bar",
                    "title": "Ticket promedio",
                    "data": [
                        {
                            "label": str(r.get("clave")),
                            "value": _num(r.get("ticket_promedio")) or 0,
                        }
                        for r in result["filas"]
                    ],
                }
            )
        elif name == "consultar_sql" and result.get("rows"):
            extra_charts.extend(_charts_from_sql_rows(result["rows"]))

    if not any(
        [kpi_payload, serie_payload, mix_payload, ranking_payload, pie_payload, extra_charts]
    ):
        return None

    scope = _infer_scope(tools)
    sucursal = scope.get("sucursal")
    anio = scope.get("anio")
    if sucursal or anio or (scope.get("desde") and scope.get("hasta")):
        try:
            kpi_payload = na.kpis_periodo(
                fecha_desde=scope.get("desde"),
                fecha_hasta=scope.get("hasta"),
                sucursal=sucursal,
                anio=anio,
            )
        except Exception:
            if not kpi_payload:
                kpi_payload = {
                    "periodo": {
                        "desde": scope.get("desde"),
                        "hasta": scope.get("hasta"),
                    },
                    "kpis": {},
                    "deltas_pct": {},
                    "sucursal": sucursal,
                }

    if not kpi_payload:
        try:
            kpi_payload = na.kpis_periodo()
        except Exception:
            period = na.default_period()
            kpi_payload = {
                "periodo": {
                    "desde": period[0].isoformat(),
                    "hasta": period[1].isoformat(),
                },
                "kpis": {},
                "deltas_pct": {},
            }

    periodo = kpi_payload.get("periodo") or {}
    desde = scope.get("desde") or periodo.get("desde")
    hasta = scope.get("hasta") or periodo.get("hasta")

    if extra_charts:
        context_serie = context_mix = context_rank = context_pie = None
        if desde and hasta:
            context_serie, context_mix, context_rank, context_pie = na.charts_for_period(
                desde, hasta, sucursal=sucursal, anio=anio
            )
        view = na.build_view_from_payloads(
            kpi_payload, context_serie, context_mix, None, context_pie
        )
        dash = view.get("charts") or []
        seen = {chart["id"] for chart in extra_charts}
        context = [chart for chart in dash if chart["id"] not in seen]
        view["charts"] = _prioritize_charts(extra_charts + context, _priority_ids(tools))
        view["source"] = "query"
        return view

    if desde and hasta:
        if not serie_payload or not mix_payload or not ranking_payload or not pie_payload:
            serie_f, mix_f, rank_f, pie_f = na.charts_for_period(
                desde, hasta, sucursal=sucursal, anio=anio
            )
            serie_payload = serie_payload or serie_f
            mix_payload = mix_payload or mix_f
            ranking_payload = ranking_payload or rank_f
            pie_payload = pie_payload or pie_f

    view = na.build_view_from_payloads(
        kpi_payload, serie_payload, mix_payload, ranking_payload, pie_payload
    )
    view["charts"] = _prioritize_charts(view.get("charts") or [], _priority_ids(tools))
    view["source"] = "query"
    return view
