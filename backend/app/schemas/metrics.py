from typing import Optional

from pydantic import BaseModel


class VentaItem(BaseModel):
    producto: str
    categoria: str
    region: str
    ventas: int


class MetricsResponse(BaseModel):
    total_ventas: int
    promedio_ventas: float
    venta_maxima: Optional[VentaItem]
    venta_minima: Optional[VentaItem]
    ventas_por_categoria: dict[str, int]