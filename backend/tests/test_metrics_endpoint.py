import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint_contra_postgres_real():
    response = client.get("/api/v1/metrics")
    if response.status_code == 503:
        pytest.skip("PostgreSQL Nortec no disponible en este entorno")

    assert response.status_code == 200

    body = response.json()
    view = body["view"]
    assert "kpis" in view
    assert isinstance(view["kpis"]["ingresos"], (int, float))
    assert isinstance(view["charts"], list)
