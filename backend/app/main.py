import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.ventas_db import ping_database
from app.services.groq_client import ask_groq_with_tools
from app.services.tools import tool_definitions, execute_tool
from app.services import nortec_analytics as na
from app.services.view_builder import infer_view_from_tools
from app.schemas.chat import ChatRequest, ChatResponse, ToolResult
from app.schemas.metrics import MetricsResponse, WorkspaceView, KpiBlock, ChartSpec


app = FastAPI(title="InsightAI")
logger = logging.getLogger(__name__)

_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_cors_origins = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", _default_origins).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ensure_db():
    ok, rows = ping_database()
    if not ok or rows is None or rows == 0:
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL no disponible o sin datos Nortec. Ejecutá seed_nortec.",
        )


def _tool_result_to_schema(entry: dict) -> ToolResult:
    result = entry.get("result")
    sql = None
    if isinstance(result, dict):
        if "sql" in result and isinstance(result["sql"], str):
            sql = result["sql"]
        elif entry.get("name") == "consultar_sql" and "sql" in result:
            sql = str(result["sql"])
    return ToolResult(
        name=entry["name"],
        arguments=entry.get("arguments") or {},
        result=result,
        sql=sql,
    )


def _dict_to_workspace(view: dict) -> WorkspaceView:
    kpis = view.get("kpis") or {}
    return WorkspaceView(
        period=view.get("period") or {},
        coverage=view.get("coverage") or None,
        kpis=KpiBlock(
            ingresos=kpis.get("ingresos"),
            margen_pct=kpis.get("margen_pct"),
            ticket=kpis.get("ticket"),
            unidades=kpis.get("unidades"),
            deltas=kpis.get("deltas"),
        ),
        charts=[ChartSpec(**c) for c in view.get("charts") or []],
        source=view.get("source"),
    )


@app.get("/")
def root():
    return {"message": "InsightAI API is running", "dataset": "nortec"}


@app.get("/health")
@app.get("/api/v1/health")
def health():
    db_ok, rows = ping_database()
    if not db_ok:
        return {"status": "degraded", "database": "down"}
    return {"status": "ok", "database": "up", "fact_ventas_rows": rows}


@app.get("/api/v1/metrics", response_model=MetricsResponse)
def metrics():
    _ensure_db()
    try:
        view = na.workspace_default_view()
    except Exception:
        logger.exception("Error al calcular métricas Nortec")
        raise HTTPException(status_code=503, detail="Error al leer métricas")
    return MetricsResponse(view=_dict_to_workspace(view))


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    _ensure_db()

    history = [{"role": h.role, "content": h.content} for h in request.history]

    def _ejecutar_herramienta(nombre, argumentos):
        return execute_tool(nombre, argumentos)

    try:
        answer, herramientas = ask_groq_with_tools(
            request.question,
            tool_definitions(),
            _ejecutar_herramienta,
            history=history,
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

    tools = [_tool_result_to_schema(h) for h in herramientas]
    view = None
    if herramientas:
        view_dict = infer_view_from_tools(herramientas)
        view = _dict_to_workspace(view_dict) if view_dict else None
    return ChatResponse(answer=answer, tools=tools, view=view)
