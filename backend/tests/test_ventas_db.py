import pytest

from app.services.ventas_db import ping_database


def test_ping_database_contra_postgres_real():
    pytest.importorskip(
        "psycopg2",
        reason="psycopg2 no está instalado; no se puede verificar la integración",
    )

    try:
        ok, rows = ping_database()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"PostgreSQL no disponible en este entorno: {exc}")

    if not ok:
        pytest.skip("PostgreSQL no disponible o sin schema Nortec")

    assert rows is not None
    assert rows > 0
