import pytest

from app.services.sql_validator import validate_readonly_select


def test_validate_select_happy_path():
    sql = validate_readonly_select(
        "SELECT categoria, SUM(ingresos) AS total FROM v_ventas_linea GROUP BY categoria"
    )
    assert "LIMIT 100" in sql.upper()


def test_validate_join_allowed():
    sql = validate_readonly_select(
        "SELECT p.nombre, SUM(f.cantidad) FROM fact_ventas f "
        "JOIN dim_producto p ON f.producto_id = p.id GROUP BY p.nombre"
    )
    assert "LIMIT 100" in sql.upper()


def test_validate_rejects_drop():
    with pytest.raises(ValueError, match="no permitidas"):
        validate_readonly_select("DROP TABLE fact_ventas")


def test_validate_rejects_non_select():
    with pytest.raises(ValueError, match="no permitidas"):
        validate_readonly_select("UPDATE fact_ventas SET cantidad = 0")


def test_validate_rejects_unknown_table():
    with pytest.raises(ValueError, match="Tabla no permitida"):
        validate_readonly_select("SELECT * FROM usuarios")


def test_validate_from_en_otra_linea():
    sql = validate_readonly_select(
        "SELECT producto, SUM(cantidad)\nFROM v_ventas_linea\nGROUP BY producto"
    )
    assert "LIMIT 100" in sql.upper()
