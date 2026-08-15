from app.services.data_analysis import (
    total_ventas,
    venta_maxima,
    venta_minima,
    ventas_por_categoria,
)


def ventas_por_region(data):
    regiones = {}
    for item in data:
        region = item["region"]
        regiones[region] = regiones.get(region, 0) + item["ventas"]
    return regiones


def ventas_filtradas(data, categoria=None, region=None):
    if categoria is not None and not isinstance(categoria, str):
        raise ValueError("El filtro 'categoria' debe ser un texto")
    if region is not None and not isinstance(region, str):
        raise ValueError("El filtro 'region' debe ser un texto")

    return [
        item
        for item in data
        if (categoria is None or item["categoria"] == categoria)
        and (region is None or item["region"] == region)
    ]


def _validar_argumentos_vacios(arguments):
    if not isinstance(arguments, dict):
        raise ValueError("Los argumentos deben ser un objeto JSON")
    if arguments:
        raise ValueError(
            f"La herramienta no acepta argumentos, pero se recibieron: {sorted(arguments)}"
        )


def _tool_total_ventas(arguments, data):
    _validar_argumentos_vacios(arguments)
    return total_ventas(data)


def _tool_ventas_por_categoria(arguments, data):
    _validar_argumentos_vacios(arguments)
    return ventas_por_categoria(data)


def _tool_ventas_por_region(arguments, data):
    _validar_argumentos_vacios(arguments)
    return ventas_por_region(data)


def _tool_venta_maxima(arguments, data):
    _validar_argumentos_vacios(arguments)
    maxima = venta_maxima(data)
    if maxima is None:
        return {"error": "No hay datos de ventas"}
    return maxima


def _tool_venta_minima(arguments, data):
    _validar_argumentos_vacios(arguments)
    minima = venta_minima(data)
    if minima is None:
        return {"error": "No hay datos de ventas"}
    return minima


def _tool_ventas_filtradas(arguments, data):
    if not isinstance(arguments, dict):
        raise ValueError("Los argumentos deben ser un objeto JSON")
    return ventas_filtradas(data, **arguments)


# Registro central de herramientas disponibles para el LLM.
# Cada entrada define el nombre, la descripción, el esquema de parámetros
# (JSON Schema que Groq usa para guiar la invocación) y la función ejecutora.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "total_ventas",
            "description": "Devuelve el total de ventas registradas en la tabla ventas.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
        "executor": _tool_total_ventas,
    },
    {
        "type": "function",
        "function": {
            "name": "ventas_por_categoria",
            "description": "Devuelve las ventas totales agrupadas por categoría de producto.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
        "executor": _tool_ventas_por_categoria,
    },
    {
        "type": "function",
        "function": {
            "name": "ventas_por_region",
            "description": "Devuelve las ventas totales agrupadas por región.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
        "executor": _tool_ventas_por_region,
    },
    {
        "type": "function",
        "function": {
            "name": "venta_maxima",
            "description": "Devuelve el producto con la mayor cantidad de ventas.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
        "executor": _tool_venta_maxima,
    },
    {
        "type": "function",
        "function": {
            "name": "venta_minima",
            "description": "Devuelve el producto con la menor cantidad de ventas.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
        "executor": _tool_venta_minima,
    },
    {
        "type": "function",
        "function": {
            "name": "ventas_filtradas",
            "description": (
                "Devuelve las ventas que coinciden con los filtros opcionales "
                "categoria y region. Sin filtros, devuelve todas las ventas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": "Filtrar por categoría (ej: Electrónica).",
                    },
                    "region": {
                        "type": "string",
                        "description": "Filtrar por región (ej: Norte, Sur).",
                    },
                },
                "additionalProperties": False,
            },
        },
        "executor": _tool_ventas_filtradas,
    },
]


def tool_definitions():
    """Solo la parte visible para el LLM (JSON Schema), sin los ejecutores."""
    return [
        {"type": tool["type"], "function": tool["function"]}
        for tool in TOOLS
    ]


def execute_tool(tool_name, arguments, data):
    """Despacha y ejecuta una herramienta.

    Valida que el nombre corresponda a una herramienta registrada y delega la
    validación de argumentos a cada ejecutor. Los resultados son datos Python
    serializables (dict/list/int) que el flujo tool-calling devolverá al LLM.
    """
    tool = next((t for t in TOOLS if t["function"]["name"] == tool_name), None)
    if tool is None:
        raise ValueError(f"Herramienta desconocida: {tool_name}")

    return tool["executor"](arguments, data)