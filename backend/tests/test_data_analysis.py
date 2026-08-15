from app.services.data_analysis import (
    total_ventas,
    promedio_ventas,
    venta_maxima,
    venta_minima,
    ventas_por_categoria,
)

SAMPLE = [
    {"producto": "Laptop", "categoria": "Electrónica", "region": "Norte", "ventas": 1500},
    {"producto": "Mouse", "categoria": "Accesorios", "region": "Sur", "ventas": 120},
    {"producto": "Teclado", "categoria": "Accesorios", "region": "Norte", "ventas": 80},
    {"producto": "Monitor", "categoria": "Electrónica", "region": "Sur", "ventas": 300},
    {"producto": "Impresora", "categoria": "Oficina", "region": "Norte", "ventas": 200},
]


def test_total_ventas():
    assert total_ventas(SAMPLE) == 2200


def test_total_ventas_vacio():
    assert total_ventas([]) == 0


def test_promedio_ventas():
    assert promedio_ventas(SAMPLE) == 440


def test_promedio_ventas_vacio():
    assert promedio_ventas([]) == 0


def test_venta_maxima():
    assert venta_maxima(SAMPLE)["ventas"] == 1500
    assert venta_maxima(SAMPLE)["producto"] == "Laptop"


def test_venta_maxima_vacio():
    assert venta_maxima([]) is None


def test_venta_minima():
    assert venta_minima(SAMPLE)["ventas"] == 80
    assert venta_minima(SAMPLE)["producto"] == "Teclado"


def test_venta_minima_vacio():
    assert venta_minima([]) is None


def test_ventas_por_categoria():
    assert ventas_por_categoria(SAMPLE) == {
        "Electrónica": 1800,
        "Accesorios": 200,
        "Oficina": 200,
    }