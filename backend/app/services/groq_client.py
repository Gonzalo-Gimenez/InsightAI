import json
import logging

from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError

from app.config import settings


_client = Groq(api_key=settings.GROQ_API_KEY)
_logger = logging.getLogger(__name__)

# Límite de rondas de tool-calling para evitar loops infinitos del LLM.
MAX_TOOL_ROUNDS = 5

_SISTEMA_PROMPT = (
    "Sos el asistente de análisis de ventas de InsightAI. "
    "El usuario pregunta sobre una tabla de ventas con las columnas: "
    "producto (texto), categoria (texto), region (texto) y ventas (entero). "
    "Para responder, usá las herramientas disponibles. "
    "Cuando una herramienta devuelve un error, comunícalo de forma clara al usuario. "
    "Respondé en el idioma del usuario."
)


def _traducir_error_groq(exc, mensaje):
    """Normaliza los errores de Groq a ValueError con mensajes útiles."""
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


def ask_groq_with_tools(question, tool_defs, execute_tool):
    """Responde una pregunta usando tool calling.

    El LLM decide qué herramientas invocar; Python las ejecuta con datos reales
    y el resultado se devuelve al LLM para que redacte la respuesta final.
    execute_tool debe recibir (tool_name, arguments) y devolver datos Python
    serializables.
    """
    messages = [
        {"role": "system", "content": _SISTEMA_PROMPT},
        {"role": "user", "content": question},
    ]

    for _round in range(MAX_TOOL_ROUNDS):
        try:
            response = _client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                tools=tool_defs,
            )
        except Exception as exc:
            raise _traducir_error_groq(exc, "Error al consultar Groq")

        if not response.choices:
            raise ValueError("Groq no devolvió opciones de respuesta")

        message = response.choices[0].message

        if not message.tool_calls:
            if not message.content:
                raise ValueError("Groq no devolvió contenido de texto")
            return message.content

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
            try:
                arguments = json.loads(call.function.arguments or "{}")
                result = execute_tool(call.function.name, arguments)
            except Exception as exc:  # noqa: BLE001
                _logger.exception("Error al ejecutar la herramienta %s", call.function.name)
                result = {"error": f"Error al ejecutar la herramienta: {exc}"}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                }
            )

    raise ValueError(
        "Groq no pudo responder tras varias rondas de herramientas. Inténtelo de nuevo."
    )