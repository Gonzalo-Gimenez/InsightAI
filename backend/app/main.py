import logging

from fastapi import FastAPI, HTTPException

from app.services.ventas_db import fetch_ventas_data
from app.services.groq_client import ask_groq_with_tools
from app.services.data_analysis import compute_metrics
from app.services.tools import tool_definitions, execute_tool
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.metrics import MetricsResponse


app = FastAPI(title="InsightAI")
logger = logging.getLogger(__name__)


@app.get("/")
def root():
    return {"message": "InsightAI API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


def _fetch_ventas_metricas():
    try:
        data = fetch_ventas_data()
    except Exception:
        logger.exception("Error al consultar PostgreSQL")
        raise HTTPException(status_code=503, detail="PostgreSQL no disponible")

    if not data:
        raise HTTPException(status_code=503, detail="PostgreSQL devolvió cero registros")

    return compute_metrics(data), data


@app.get("/api/v1/metrics", response_model=MetricsResponse)
def metrics():
    metricas, _ = _fetch_ventas_metricas()
    return metricas


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        data = fetch_ventas_data()
    except Exception:
        logger.exception("Error al consultar PostgreSQL")
        raise HTTPException(status_code=503, detail="PostgreSQL no disponible")

    if not data:
        raise HTTPException(status_code=503, detail="PostgreSQL devolvió cero registros")

    def _ejecutar_herramienta(nombre, argumentos):
        return execute_tool(nombre, argumentos, data)

    try:
        answer = ask_groq_with_tools(
            request.question,
            tool_definitions(),
            _ejecutar_herramienta,
        )
    except ValueError as e:
        msg = str(e)
        if "autenticación" in msg:
            raise HTTPException(status_code=401, detail=msg)
        if "Límite de velocidad" in msg:
            raise HTTPException(status_code=429, detail=msg)
        if "conectar" in msg:
            raise HTTPException(status_code=503, detail=msg)
        raise HTTPException(status_code=500, detail=msg)

    return {"answer": answer}