from unittest.mock import patch

import pytest

from app.services.tools import tool_definitions, execute_tool


def test_tool_definitions_solo_json_schema():
    defs = tool_definitions()
    assert len(defs) >= 10
    for tool in defs:
        assert tool["type"] == "function"
        assert "name" in tool["function"]
        assert "executor" not in tool


def test_tool_definitions_incluyen_nortec():
    nombres = {t["function"]["name"] for t in tool_definitions()}
    assert "kpis_periodo" in nombres
    assert "consultar_sql" in nombres
    assert "listar_esquema" in nombres


@patch("app.services.tools.na.listar_esquema")
def test_execute_listar_esquema(mock_listar):
    mock_listar.return_value = {"tablas": ["fact_ventas"]}
    result = execute_tool("listar_esquema", {})
    assert result["tablas"] == ["fact_ventas"]


@patch("app.services.tools.run_validated_select")
@patch("app.services.tools.validate_readonly_select")
def test_execute_consultar_sql(mock_validate, mock_run):
    mock_validate.return_value = "SELECT 1"
    mock_run.return_value = [{"x": 1}]
    result = execute_tool("consultar_sql", {"sql": "SELECT 1 FROM v_ventas_linea"})
    assert result["count"] == 1


def test_tools_no_exponen_fechas():
    for tool in tool_definitions():
        props = tool["function"]["parameters"].get("properties") or {}
        assert "fecha_desde" not in props
        assert "fecha_hasta" not in props


@patch("app.services.tools.na.serie_mensual")
def test_execute_omite_fechas_null(mock_serie):
    mock_serie.return_value = {"serie": []}
    execute_tool(
        "serie_mensual",
        {"fecha_desde": None, "fecha_hasta": None, "metrica": "ingresos"},
    )
    mock_serie.assert_called_once_with(
        fecha_desde=None,
        fecha_hasta=None,
        metrica="ingresos",
        meses=None,
        sucursal=None,
        anio=None,
    )


def test_tools_exponen_sucursal_y_anio():
    scoped = {
        "kpis_periodo",
        "serie_mensual",
        "ranking_productos",
        "mix_categoria",
        "mix_region",
        "mix_canal",
    }
    for tool in tool_definitions():
        name = tool["function"]["name"]
        if name not in scoped:
            continue
        props = tool["function"]["parameters"].get("properties") or {}
        assert "sucursal" in props, name
        assert "anio" in props, name


def test_execute_tool_desconocido():
    with pytest.raises(ValueError, match="Herramienta desconocida"):
        execute_tool("no_existe", {})