import json
import logging
import re

from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError

from app.config import settings


_client = Groq(api_key=settings.GROQ_API_KEY)
_logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 6


def _sistema_prompt() -> str:
    rango = ""
    try:
        from app.services.nortec_analytics import date_bounds

        desde, hasta = date_bounds()
        rango = (
            f" Los datos van de {desde.isoformat()} a {hasta.isoformat()}. "
            "KPIs: últimos 30 días. serie_mensual usa meses (entero): 5 = mes actual y 4 anteriores. "
            "Nunca envíes null ni fecha_desde/fecha_hasta. Omití las claves que no uses. "
        )
    except Exception:
        rango = " serie_mensual acepta meses (entero). Nunca envíes null. "

    return (
        "Sos el copiloto analítico de Nortec (retail electrónica Latam) en InsightAI. "
        "Datos en PostgreSQL: dim_tiempo, dim_producto, dim_cliente, dim_sucursal, "
        "fact_ventas y v_ventas_linea (columnas: producto, sku, categoria, ingresos, margen, "
        "cantidad, fecha, region, canal, sucursal)."
        f"{rango}"
        "Reglas estrictas: "
        "1) Si el usuario saluda o no pide un análisis, respondé breve y NO invoques herramientas. "
        "2) Si pide cifras, rankings, mix o tendencias, invocá tools en el primer turno y el canvas se actualiza solo. "
        "Si mencionan una sede (Belgrano), 'dicha sede' o un año (2024), pasá sucursal y anio en kpis_periodo, "
        "serie_mensual, mix_* y ranking_productos. Los 4 gráficos y los KPIs se recortan a ese alcance; "
        "nunca dejes el canvas en el histórico global. No esperes a que pidan verlo en el gráfico. "
        "3) Nunca inventes números. "
        "4) Top N / más vendidos → ranking_productos (limite). Mix top N → mix_categoria(limite=N). "
        "Un COUNT de sucursales o tickets se responde en texto; no uses consultar_sql para eso si alcanza una tool. "
        "5) Si piden 'mostralo en el gráfico', volvé a invocar la tool. Nunca digas que no podés generar un gráfico. "
        "6) consultar_sql solo ad-hoc: SELECT ... FROM v_ventas_linea. La columna se llama producto. "
        "Top N de una sede/año → ranking_productos(sucursal, anio), no SQL. "
        "7) Regiones: Norte, Cuyo, Litoral, AMBA, Patagonia. Canales: tienda, online. "
        "8) Sucursales físicas = canal tienda. Outlet / Tienda Online AR = canal online. "
        "9) Respondé en el idioma del usuario, texto plano, sin markdown. "
    )


def _traducir_error_groq(exc, mensaje):
    if isinstance(exc, AuthenticationError):
        _logger.exception(mensaje)
        return ValueError("Error de autenticación con el servicio de Groq")
    if isinstance(exc, RateLimitError):
        _logger.exception(mensaje)
        return ValueError("Límite de velocidad alcanzado, inténtelo de nuevo más tarde")
    if isinstance(exc, APIConnectionError):
        _logger.exception(mensaje)
        return ValueError("No se pudo conectar con el servicio de Groq")
    _logger.exception(mensaje)
    return ValueError("Error inesperado al consultar Groq")


def _failed_generation(exc) -> dict | None:
    blobs: list[dict] = []
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        blobs.append(body)
    response = getattr(exc, "response", None)
    if response is not None:
        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                blobs.append(parsed)
        except Exception:
            pass
    raw = None
    for blob in blobs:
        err = blob.get("error")
        if isinstance(err, dict) and isinstance(err.get("failed_generation"), str):
            raw = err["failed_generation"]
            break
    if raw is None:
        match = re.search(
            r"failed_generation['\"]?\s*[:=]\s*['\"](\{.*\})['\"]",
            str(exc),
            re.DOTALL,
        )
        if match:
            raw = match.group(1)
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or not payload.get("name"):
        return None
    arguments = payload.get("arguments") or {}
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = {}
    if not isinstance(arguments, dict):
        arguments = {}
    return {"name": payload["name"], "arguments": arguments}


def _allowed_properties(tool_defs, name: str) -> set[str] | None:
    for tool in tool_defs:
        function = tool.get("function") or {}
        if function.get("name") == name:
            props = (function.get("parameters") or {}).get("properties") or {}
            return set(props)
    return None


def _sanitize_arguments(name: str, arguments: dict, tool_defs) -> dict:
    allowed = _allowed_properties(tool_defs, name)
    cleaned = {}
    for key, value in arguments.items():
        if value is None:
            continue
        if allowed is not None and key not in allowed:
            continue
        cleaned[key] = value
    return cleaned


def _append_tool_turn(messages, call_id: str, name: str, arguments: dict, result):
    messages.append(
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(arguments, ensure_ascii=False),
                    },
                }
            ],
        }
    )
    messages.append(
        {
            "role": "tool",
            "tool_call_id": call_id,
            "content": json.dumps(result, ensure_ascii=False, default=str),
        }
    )


def ask_groq_with_tools(question, tool_defs, execute_tool, history=None):
    messages = [{"role": "system", "content": _sistema_prompt()}]
    if history:
        for item in history[-10:]:
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": question})
    herramientas_ejecutadas = []

    for round_idx in range(MAX_TOOL_ROUNDS):
        try:
            response = _client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                tools=tool_defs,
            )
        except Exception as exc:
            failed = _failed_generation(exc)
            if failed:
                name = failed["name"]
                arguments = _sanitize_arguments(name, failed["arguments"], tool_defs)
                try:
                    result = execute_tool(name, arguments)
                except Exception as tool_exc:  # noqa: BLE001
                    _logger.warning("Tool recuperada %s falló: %s", name, tool_exc)
                    result = {"error": f"Error al ejecutar la herramienta: {tool_exc}"}
                _append_tool_turn(
                    messages, f"recovered_{round_idx}", name, arguments, result
                )
                herramientas_ejecutadas.append(
                    {"name": name, "arguments": arguments, "result": result}
                )
                continue
            raise _traducir_error_groq(exc, "Error al consultar Groq")

        if not response.choices:
            raise ValueError("Groq no devolvió opciones de respuesta")

        message = response.choices[0].message

        if not message.tool_calls:
            if not message.content:
                raise ValueError("Groq no devolvió contenido de texto")
            return message.content, herramientas_ejecutadas

        assistant_message = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        }
        messages.append(assistant_message)

        for call in message.tool_calls:
            arguments: dict = {}
            try:
                parsed = json.loads(call.function.arguments or "{}")
                arguments = parsed if isinstance(parsed, dict) else {}
                arguments = _sanitize_arguments(call.function.name, arguments, tool_defs)
                result = execute_tool(call.function.name, arguments)
            except Exception as exc:  # noqa: BLE001
                _logger.warning(
                    "Error al ejecutar la herramienta %s: %s",
                    call.function.name,
                    exc,
                )
                result = {"error": f"Error al ejecutar la herramienta: {exc}"}

            herramientas_ejecutadas.append(
                {"name": call.function.name, "arguments": arguments, "result": result}
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                }
            )

    if herramientas_ejecutadas:
        ok = any(
            isinstance(item.get("result"), dict) and not item["result"].get("error")
            for item in herramientas_ejecutadas
        )
        if ok:
            return (
                "Consulté los datos. El canvas muestra el recorte; si querés otro, preguntá de nuevo.",
                herramientas_ejecutadas,
            )
        return (
            "No pude completar esa consulta con las herramientas. Probá de nuevo o pedilo como ranking o mix.",
            herramientas_ejecutadas,
        )
    raise ValueError(
        "Groq no pudo responder tras varias rondas de herramientas. Inténtelo de nuevo."
    )
