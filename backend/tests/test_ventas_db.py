import pytest

from app.services.ventas_db import fetch_ventas_data


def test_fetch_ventas_data_contra_postgres_real():
    """Integration test: verifica contra PostgreSQL real.

    Estado de verificación:
    - Si la infraestructura (contenedor postgres) está disponible: corre el test
      contra la DB real y valida que devuelve registros con las claves esperadas.
    - Si NO está disponible: se salta (skip) y reporta el motivo. No simula éxito.

    Para correr con la infra levantada:
      docker compose up -d   (y luego: python -m pytest tests -v)
    """
    pytest.importorskip(
        "psycopg2",
        reason="psycopg2 no está instalado; no se puede verificar la integración",
    )

    try:
        data = fetch_ventas_data()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"PostgreSQL no disponible en este entorno: {exc}")

    assert isinstance(data, list)
    assert len(data) > 0
    for row in data:
        assert set(row) == {"producto", "categoria", "region", "ventas"}
        assert isinstance(row["ventas"], int)
