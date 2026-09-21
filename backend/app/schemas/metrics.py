from typing import Any, Optional

from pydantic import BaseModel


class KpiBlock(BaseModel):
    ingresos: Optional[float] = None
    margen_pct: Optional[float] = None
    ticket: Optional[float] = None
    unidades: Optional[int] = None
    deltas: Optional[dict[str, Optional[float]]] = None


class ChartSpec(BaseModel):
    id: str
    type: str
    title: str
    data: list[Any] = []


class WorkspaceView(BaseModel):
    period: dict[str, Optional[str]]
    coverage: Optional[dict[str, Optional[str]]] = None
    kpis: KpiBlock
    charts: list[ChartSpec] = []
    source: Optional[str] = None


class MetricsResponse(BaseModel):
    view: WorkspaceView
