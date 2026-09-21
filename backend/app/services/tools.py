from app.services import nortec_analytics as na
from app.services.sql_validator import validate_readonly_select
from app.services.ventas_db import run_validated_select


def _require_dict(arguments):
    if not isinstance(arguments, dict):
        raise ValueError("Los argumentos deben ser un objeto JSON")
    return arguments


def _tool_listar_esquema(arguments, _data=None):
    _require_dict(arguments)
    return na.listar_esquema()


def _tool_describir_tabla(arguments, _data=None):
    args = _require_dict(arguments)
    tabla = args.get("tabla")
    if not isinstance(tabla, str) or not tabla.strip():
        raise ValueError("El argumento 'tabla' es obligatorio")
    return na.describir_tabla(tabla.strip())


def _tool_kpis_periodo(arguments, _data=None):
    args = _require_dict(arguments)
    return na.kpis_periodo(
        fecha_desde=args.get("fecha_desde"),
        fecha_hasta=args.get("fecha_hasta"),
        region=args.get("region"),
        categoria=args.get("categoria"),
        canal=args.get("canal"),
        sucursal=args.get("sucursal"),
        anio=args.get("anio"),
    )


def _tool_serie_mensual(arguments, _data=None):
    args = _require_dict(arguments)
    return na.serie_mensual(
        fecha_desde=args.get("fecha_desde"),
        fecha_hasta=args.get("fecha_hasta"),
        metrica=args.get("metrica") or "ingresos",
        meses=args.get("meses"),
        sucursal=args.get("sucursal"),
        anio=args.get("anio"),
    )


def _tool_ranking_productos(arguments, _data=None):
    args = _require_dict(arguments)
    return na.ranking_productos(
        limite=args.get("limite") or 10,
        orden=args.get("orden") or "ingresos",
        fecha_desde=args.get("fecha_desde"),
        fecha_hasta=args.get("fecha_hasta"),
        region=args.get("region"),
        sucursal=args.get("sucursal"),
        anio=args.get("anio"),
    )


def _tool_mix_categoria(arguments, _data=None):
    args = _require_dict(arguments)
    return na.mix_dimension(
        "categoria",
        args.get("fecha_desde"),
        args.get("fecha_hasta"),
        limite=args.get("limite"),
        sucursal=args.get("sucursal"),
        anio=args.get("anio"),
    )


def _tool_mix_region(arguments, _data=None):
    args = _require_dict(arguments)
    return na.mix_dimension(
        "region",
        args.get("fecha_desde"),
        args.get("fecha_hasta"),
        limite=args.get("limite"),
        sucursal=args.get("sucursal"),
        anio=args.get("anio"),
    )


def _tool_mix_canal(arguments, _data=None):
    args = _require_dict(arguments)
    return na.mix_dimension(
        "canal",
        args.get("fecha_desde"),
        args.get("fecha_hasta"),
        sucursal=args.get("sucursal"),
        anio=args.get("anio"),
    )


def _tool_ticket_promedio(arguments, _data=None):
    args = _require_dict(arguments)
    return na.ticket_promedio_por(
        agrupar=args.get("agrupar") or "region",
        fecha_desde=args.get("fecha_desde"),
        fecha_hasta=args.get("fecha_hasta"),
    )


def _tool_comparar_periodos(arguments, _data=None):
    args = _require_dict(arguments)
    return na.comparar_periodos(
        fecha_desde=args.get("fecha_desde"),
        fecha_hasta=args.get("fecha_hasta"),
    )


def _tool_consultar_sql(arguments, _data=None):
    args = _require_dict(arguments)
    sql = args.get("sql")
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("El argumento 'sql' debe ser un SELECT no vacío")
    validated = validate_readonly_select(sql)
    rows = run_validated_select(validated)
    return {"sql": validated, "rows": rows, "count": len(rows)}


_EMPTY_PARAMS = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}

_LIMIT_PARAMS = {
    "type": "object",
    "properties": {
        "limite": {
            "type": "integer",
            "description": "Top N barras. 3 = las 3 de mayor ingreso.",
        },
        "sucursal": {"type": "string", "description": "Nombre de sede, ej. Belgrano"},
        "anio": {"type": "integer", "description": "Año calendario, ej. 2024"},
    },
    "additionalProperties": False,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "listar_esquema",
            "description": "Lista tablas y columnas del warehouse Nortec.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        "executor": _tool_listar_esquema,
    },
    {
        "type": "function",
        "function": {
            "name": "describir_tabla",
            "description": "Describe columnas de una tabla permitida.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tabla": {
                        "type": "string",
                        "description": "dim_tiempo, dim_producto, dim_cliente, dim_sucursal, fact_ventas, v_ventas_linea",
                    }
                },
                "required": ["tabla"],
                "additionalProperties": False,
            },
        },
        "executor": _tool_describir_tabla,
    },
    {
        "type": "function",
        "function": {
            "name": "kpis_periodo",
            "description": (
                "KPIs del período: ingresos, margen, unidades, ticket promedio y deltas vs período anterior."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string"},
                    "categoria": {"type": "string"},
                    "canal": {"type": "string", "description": "tienda u online"},
                    "sucursal": {"type": "string", "description": "Nombre de sede, ej. Belgrano"},
                    "anio": {"type": "integer", "description": "Año calendario, ej. 2024"},
                },
                "additionalProperties": False,
            },
        },
        "executor": _tool_kpis_periodo,
    },
    {
        "type": "function",
        "function": {
            "name": "serie_mensual",
            "description": "Serie mensual de ingresos o margen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metrica": {
                        "type": "string",
                        "description": "ingresos o margen",
                    },
                    "meses": {
                        "type": "integer",
                        "description": "Meses hacia atrás incluyendo el actual. 5 = este mes y los 4 anteriores.",
                    },
                    "sucursal": {"type": "string", "description": "Nombre de sede, ej. Belgrano"},
                    "anio": {"type": "integer", "description": "Año calendario, ej. 2024"},
                },
                "additionalProperties": False,
            },
        },
        "executor": _tool_serie_mensual,
    },
    {
        "type": "function",
        "function": {
            "name": "ranking_productos",
            "description": "Top N productos por ingresos o margen. Usar esto para 'más vendidos' / ranking; no consultar_sql.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limite": {"type": "integer"},
                    "orden": {"type": "string", "description": "ingresos o margen"},
                    "region": {"type": "string", "description": "Norte, Cuyo, Litoral, AMBA, Patagonia"},
                    "sucursal": {"type": "string", "description": "Nombre de sede, ej. Belgrano"},
                    "anio": {"type": "integer", "description": "Año calendario, ej. 2024"},
                },
                "additionalProperties": False,
            },
        },
        "executor": _tool_ranking_productos,
    },
    {
        "type": "function",
        "function": {
            "name": "mix_categoria",
            "description": "Ingresos por categoría. Pasá limite=3 para el top 3. Actualiza el gráfico de barras.",
            "parameters": _LIMIT_PARAMS,
        },
        "executor": _tool_mix_categoria,
    },
    {
        "type": "function",
        "function": {
            "name": "mix_region",
            "description": "Ingresos por región. Pasá limite para el top N. Actualiza el gráfico de barras.",
            "parameters": _LIMIT_PARAMS,
        },
        "executor": _tool_mix_region,
    },
    {
        "type": "function",
        "function": {
            "name": "mix_canal",
            "description": "Ingresos por canal (tienda vs online). Actualiza el gráfico de dona.",
            "parameters": _LIMIT_PARAMS,
        },
        "executor": _tool_mix_canal,
    },
    {
        "type": "function",
        "function": {
            "name": "ticket_promedio",
            "description": "Ticket promedio agrupado por región, segmento o sucursal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agrupar": {
                        "type": "string",
                        "description": "region, segmento o sucursal",
                    },
                },
                "additionalProperties": False,
            },
        },
        "executor": _tool_ticket_promedio,
    },
    {
        "type": "function",
        "function": {
            "name": "comparar_periodos",
            "description": "Compara KPIs del período con el período anterior de igual duración.",
            "parameters": _EMPTY_PARAMS,
        },
        "executor": _tool_comparar_periodos,
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_sql",
            "description": (
                "SELECT de una sola sentencia sobre v_ventas_linea. "
                "Columnas: producto, sku, categoria, ingresos, margen, cantidad, fecha, region, canal, sucursal. "
                "Debe incluir FROM. No uses nombre_producto. "
                "Top N de una sede/año: ranking_productos(sucursal, anio), no SQL."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SELECT ... FROM v_ventas_linea. LIMIT máx 100. Columna de nombre: producto.",
                    }
                },
                "required": ["sql"],
                "additionalProperties": False,
            },
        },
        "executor": _tool_consultar_sql,
    },
]


def tool_definitions():
    return [{"type": tool["type"], "function": tool["function"]} for tool in TOOLS]


def execute_tool(tool_name, arguments, data=None):
    tool = next((t for t in TOOLS if t["function"]["name"] == tool_name), None)
    if tool is None:
        raise ValueError(f"Herramienta desconocida: {tool_name}")
    if isinstance(arguments, dict):
        arguments = {key: value for key, value in arguments.items() if value is not None}
    return tool["executor"](arguments, data)
