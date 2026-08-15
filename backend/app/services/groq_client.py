import logging

from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError

from app.config import settings


_client = Groq(api_key=settings.GROQ_API_KEY)
_logger = logging.getLogger(__name__)


def ask_groq_with_context(question: str, context: str) -> str:
    combined = (
        "Pregunta del usuario: {question}\n\n"
        "Hechos calculados por Python (utilice solo estos valores, no los modifique ni los invente):\n"
        "{context}\n\n"
        "Responda la pregunta basándose únicamente en los hechos de arriba. "
        "No invente números ni realice cálculos adicionales."
    ).format(question=question, context=context)

    try:
        response = _client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": combined}],
        )
    except AuthenticationError:
        _logger.exception("Error de autenticación al consultar Groq")
        raise ValueError("Error de autenticación con el servicio de Groq")
    except RateLimitError:
        _logger.exception("Límite de velocidad alcanzado al consultar Groq")
        raise ValueError("Límite de velocidad alcanzado, inténtelo de nuevo más tarde")
    except APIConnectionError:
        _logger.exception("Fallo de conexión al consultar Groq")
        raise ValueError("No se pudo conectar con el servicio de Groq")
    except Exception:
        _logger.exception("Error inesperado al consultar Groq")
        raise ValueError("Error inesperado al consultar Groq")

    # Validación defensiva de la respuesta
    if not response.choices:
        raise ValueError("Groq no devolvió opciones de respuesta")

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Groq no devolvió contenido de texto")

    return content