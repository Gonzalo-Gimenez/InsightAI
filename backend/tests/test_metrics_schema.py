from app.schemas.metrics import MetricsResponse, WorkspaceView, KpiBlock, ChartSpec


def test_metrics_response_valida_workspace():
    payload = {
        "view": {
            "period": {"from": "2025-01-01", "to": "2025-01-31"},
            "kpis": {
                "ingresos": 1000.5,
                "margen_pct": 12.3,
                "ticket": 45.0,
                "unidades": 200,
                "deltas": {"ingresos": 5.2},
            },
            "charts": [
                {
                    "id": "serie",
                    "type": "line",
                    "title": "Serie",
                    "data": [{"label": "2025-01", "valor": 100}],
                }
            ],
        }
    }
    m = MetricsResponse.model_validate(payload)
    assert m.view.kpis.ingresos == 1000.5
    assert m.view.charts[0].type == "line"


def test_workspace_view_minimo():
    w = WorkspaceView(
        period={"from": "2024-01-01", "to": "2024-01-31"},
        kpis=KpiBlock(),
        charts=[],
    )
    assert w.period["from"] == "2024-01-01"
