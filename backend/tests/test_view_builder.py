from unittest.mock import patch

from app.services.view_builder import (
    _charts_from_sql_rows,
    _infer_scope,
    _prioritize_charts,
    infer_view_from_tools,
)


def test_catalog_sql_skips_id_bar():
    rows = [{"id": i, "nombre": f"Sede {i}"} for i in range(1, 13)]
    charts = _charts_from_sql_rows(rows)
    assert len(charts) == 1
    assert charts[0]["type"] == "table"
    assert len(charts[0]["data"]) == 12
    assert charts[0]["title"] == "Resultado (12)"


def test_count_sql_no_roba_un_tile():
    charts = _charts_from_sql_rows([{"sedes": 12}])
    assert charts == []


def test_metric_sql_gets_bar_and_table():
    rows = [
        {"nombre": "Smartphones", "ingresos": 800_000},
        {"nombre": "Audio", "ingresos": 200_000},
    ]
    charts = _charts_from_sql_rows(rows)
    assert [c["type"] for c in charts] == ["bar", "table"]
    assert charts[0]["data"][0]["value"] == 800_000


@patch("app.services.view_builder.na.build_view_from_payloads")
@patch("app.services.view_builder.na.charts_for_period")
@patch("app.services.view_builder.na.kpis_periodo")
def test_list_query_does_not_inflate_canvas(mock_kpis, mock_charts, mock_build):
    mock_kpis.return_value = {
        "periodo": {"desde": "2025-08-01", "hasta": "2025-08-31"},
        "kpis": {},
        "deltas_pct": {},
    }
    mock_charts.return_value = ({}, {}, {}, {})
    mock_build.return_value = {
        "charts": [
            {"id": "serie_mensual", "type": "line", "title": "Ingresos", "data": [1]},
            {"id": "mix_categoria", "type": "bar", "title": "Mix", "data": [1]},
            {"id": "mix_canal", "type": "pie", "title": "Canal", "data": [1]},
        ]
    }
    sucursales = [{"id": i, "nombre": f"Sede {i}"} for i in range(1, 13)]
    view = infer_view_from_tools(
        [{"name": "consultar_sql", "result": {"rows": sucursales, "count": 12}}]
    )
    assert view is not None
    assert all(c.get("id") != "sql_result" for c in view["charts"])
    table = next(c for c in view["charts"] if c["id"] == "sql_table")
    assert len(table["data"]) == 12
    assert len(view["charts"]) == 4


def test_prioritize_pone_el_mix_adelante():
    charts = [
        {"id": "serie_mensual", "type": "line"},
        {"id": "mix_categoria", "type": "bar"},
        {"id": "mix_canal", "type": "pie"},
        {"id": "ranking_productos", "type": "table"},
    ]
    ordered = _prioritize_charts(charts, ["mix_categoria"])
    assert [c["id"] for c in ordered][0] == "mix_categoria"


def test_infer_scope_desde_sql_sede_y_extract_year():
    sql = (
        "SELECT producto, SUM(ingresos) AS ingresos_total "
        "FROM v_ventas_linea "
        "WHERE sucursal = 'Belgrano' "
        "AND EXTRACT(YEAR FROM fecha) = 2024 "
        "GROUP BY producto"
    )
    scope = _infer_scope(
        [{"name": "consultar_sql", "arguments": {"sql": sql}, "result": {"sql": sql}}]
    )
    assert scope["sucursal"] == "Belgrano"
    assert scope["anio"] == 2024
    assert scope["desde"] == "2024-01-01"
    assert scope["hasta"] == "2024-12-31"


def test_infer_scope_desde_args_de_tool():
    scope = _infer_scope(
        [
            {
                "name": "ranking_productos",
                "arguments": {"sucursal": "Belgrano", "anio": 2024, "limite": 10},
                "result": {"top": [], "sucursal": "Belgrano"},
            }
        ]
    )
    assert scope["sucursal"] == "Belgrano"
    assert scope["anio"] == 2024


@patch("app.services.view_builder.na.build_view_from_payloads")
@patch("app.services.view_builder.na.charts_for_period")
@patch("app.services.view_builder.na.kpis_periodo")
def test_sql_sede_anio_recorta_todo_el_canvas(mock_kpis, mock_charts, mock_build):
    mock_kpis.return_value = {
        "periodo": {"desde": "2024-01-01", "hasta": "2024-12-31"},
        "kpis": {"ingresos": 1},
        "deltas_pct": {},
        "sucursal": "Belgrano",
    }
    mock_charts.return_value = ({}, {}, {}, {})
    mock_build.return_value = {
        "charts": [
            {"id": "serie_mensual", "type": "line", "title": "Ingresos", "data": [1]},
            {"id": "mix_categoria", "type": "bar", "title": "Mix", "data": [1]},
            {"id": "mix_canal", "type": "pie", "title": "Canal", "data": [1]},
        ]
    }
    sql = (
        "SELECT producto, SUM(ingresos) AS ingresos_total "
        "FROM v_ventas_linea WHERE sucursal = 'Belgrano' "
        "AND EXTRACT(YEAR FROM fecha) = 2024 GROUP BY 1"
    )
    rows = [
        {"producto": "Pulse Gama media 152", "ingresos_total": 70698.02},
        {"producto": "Pulse Laptops 3", "ingresos_total": 43743.96},
    ]
    view = infer_view_from_tools(
        [
            {
                "name": "consultar_sql",
                "arguments": {"sql": sql},
                "result": {"sql": sql, "rows": rows, "count": 2},
            }
        ]
    )
    assert view is not None
    mock_kpis.assert_called()
    kpi_kwargs = mock_kpis.call_args.kwargs
    assert kpi_kwargs["sucursal"] == "Belgrano"
    assert kpi_kwargs["anio"] == 2024
    chart_kwargs = mock_charts.call_args.kwargs
    assert chart_kwargs["sucursal"] == "Belgrano"
    assert chart_kwargs["anio"] == 2024
