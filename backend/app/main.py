import logging

from fastapi import FastAPI, HTTPException

from app.services.ventas_db import fetch_ventas_data
from app.services.groq_client import ask_groq_with_context
from app.services.data_analysis import total_ventas, promedio_ventas, venta_maxima, venta_minima, ventas_por_categoria
from app.schemas.chat import ChatRequest, ChatResponse


app = FastAPI(title="InsightAI")
logger = logging.getLogger(__name__)


@app.get("/")
def root():
    return {"message": "InsightAI API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        data = fetch_ventas_data()
    except Exception:
        logger.exception("Error al consultar PostgreSQL")
        raise HTTPException(status_code=503, detail="PostgreSQL no disponible")

    if not data:
        raise HTTPException(status_code=503, detail="PostgreSQL devolvió cero registros")

    total = total_ventas(data)
    promedio = promedio_ventas(data)
    maxima = venta_maxima(data)
    minima = venta_minima(data)
    por_categoria = ventas_por_categoria(data)

    contexto = (
        f"Total de ventas: {total}\n"
        f"Promedio de ventas: {promedio}\n"
        f"Venta máxima: {maxima['producto']} — {maxima['ventas']}\n"
        f"Venta mínima: {minima['producto']} — {minima['ventas']}\n"
        f"Ventas por categoría:\n"
    )
    for cat, val in por_categoria.items():
        contexto += f"- {cat}: {val}\n"

    try:
        answer = ask_groq_with_context(request.question, contexto)
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