import pytest

from app.services.tools import (
    tool_definitions,
    execute_tool,
    ventas_por_region,
    ventas_filtradas,
)

SAMPLE = [
    {"producto": "Laptop", "categoria": "Electrónica", "region": "Norte", "ventas": 1500},
    {"producto": "Mouse", "categoria": "Accesorios", "region": "Sur", "ventas": 120},
    {"producto": "Teclado", "categoria": "Accesorios", "region": "Norte", "ventas": 80},
    {"producto": "Monitor", "categoria": "Electrónica", "region": "Sur", "ventas": 300},
    {"producto": "Impresora", "categoria": "Oficina", "region": "Norte", "ventas": 200},
]


def test_tool_definitions_solo_json_schema():
    defs = tool_definitions()
    assert len(defs) == 6
    for tool in defs:
        assert tool["type"] == "function"
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]
        assert "executor" not in tool


def test_tool_definitions_incluyen_herramientas_esperadas():
    nombres = {t["function"]["name"] for t in tool_definitions()}
    assert nombres == {
        "total_ventas",
        "ventas_por_categoria",
        "ventas_por_region",
        "venta_maxima",
        "venta_minima",
        "ventas_filtradas",
    }


def test_execute_total_ventas():
    assert execute_tool("total_ventas", {}, SAMPLE) == 2200


def test_execute_ventas_por_categoria():
    assert execute_tool("ventas_por_categoria", {}, SAMPLE) == {
        "Electrónica": 1800,
        "Accesorios": 200,
        "Oficina": 200,
    }


def test_execute_ventas_por_region():
    assert execute_tool("ventas_por_region", {}, SAMPLE) == {
        "Norte": 1780,
        "Sur": 420,
    }


def test_execute_venta_maxima():
    assert execute_tool("venta_maxima", {}, SAMPLE)["producto"] == "Laptop"
    assert execute_tool("venta_maxima", {}, SAMPLE)["ventas"] == 1500


def test_execute_venta_minima():
    assert execute_tool("venta_minima", {}, SAMPLE)["producto"] == "Teclado"
    assert execute_tool("venta_minima", {}, SAMPLE)["ventas"] == 80


def test_execute_ventas_filtradas_por_categoria():
    resultado = execute_tool(
        "ventas_filtradas", {"categoria": "Electrónica"}, SAMPLE
    )
    assert [r["producto"] for r in resultado] == ["Laptop", "Monitor"]


def test_execute_ventas_filtradas_por_region():
    resultado = execute_tool("ventas_filtradas", {"region": "Sur"}, SAMPLE)
    assert [r["producto"] for r in resultado] == ["Mouse", "Monitor"]


def test_execute_ventas_filtradas_sin_filtros_devuelve_todo():
    resultado = execute_tool("ventas_filtradas", {}, SAMPLE)
    assert len(resultado) == 5


def test_execute_ventas_filtradas_con_ambos_filtros():
    resultado = execute_tool(
        "ventas_filtradas", {"categoria": "Electrónica", "region": "Sur"}, SAMPLE
    )
    assert [r["producto"] for r in resultado] == ["Monitor"]


def test_execute_tool_desconocido():
    with pytest.raises(ValueError, match="Herramienta desconocida"):
        execute_tool("no_existe", {}, SAMPLE)


def test_execute_tool_herramienta_sin_args_rechaza_argumentos():
    with pytest.raises(ValueError):
        execute_tool("total_ventas", {"categoria": "Electrónica"}, SAMPLE)


def test_ventas_filtradas_valida_tipos():
    with pytest.raises(ValueError, match="categoria"):
        ventas_filtradas(SAMPLE, categoria=123)
    with pytest.raises(ValueError, match="region"):
        ventas_filtradas(SAMPLE, region=42)


def test_ventas_filtradas_sin_match_devuelve_vacio():
    assert ventas_filtradas(SAMPLE, categoria="Inexistente") == []
