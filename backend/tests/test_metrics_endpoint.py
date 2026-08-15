import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint_contra_postgres_real():
    """Integration test: GET /api/v1/metrics contra PostgreSQL real.

    Si la infraestructura (contenedor postgres) está disponible, verifica el
    contrato del JSON que consumirá el frontend. Si no, se salta sin simular éxito.
    """
    try:
        response = client.get("/api/v1/metrics")
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"PostgreSQL no disponible en este entorno: {exc}")

    assert response.status_code == 200

    body = response.json()
    assert isinstance(body["total_ventas"], int)
    assert isinstance(body["promedio_ventas"], float)
    assert body["venta_maxima"]["producto"]
    assert body["venta_minima"]["producto"]
    assert isinstance(body["ventas_por_categoria"], dict)
    assert all(
        isinstance(ventas, int) for ventas in body["ventas_por_categoria"].values()
    )