from app.schemas.metrics import MetricsResponse


def test_metrics_response_valida_payload_completo():
    payload = {
        "total_ventas": 2200,
        "promedio_ventas": 440.0,
        "venta_maxima": {"producto": "Laptop", "categoria": "Electrónica", "region": "Norte", "ventas": 1500},
        "venta_minima": {"producto": "Teclado", "categoria": "Accesorios", "region": "Norte", "ventas": 80},
        "ventas_por_categoria": {"Electrónica": 1800, "Accesorios": 200, "Oficina": 200},
    }
    m = MetricsResponse.model_validate(payload)
    assert m.total_ventas == 2200
    assert m.venta_maxima.producto == "Laptop"
    assert m.ventas_por_categoria["Electrónica"] == 1800


def test_metrics_response_acepta_ventas_max_min_nulo():
    payload = {
        "total_ventas": 0,
        "promedio_ventas": 0.0,
        "venta_maxima": None,
        "venta_minima": None,
        "ventas_por_categoria": {},
    }
    m = MetricsResponse.model_validate(payload)
    assert m.venta_maxima is None
    assert m.venta_minima is None