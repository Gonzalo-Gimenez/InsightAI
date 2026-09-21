from decimal import Decimal

import psycopg2

from app.config import settings

STATEMENT_TIMEOUT_MS = 15_000


def _connect(readonly: bool = False):
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    if readonly and settings.POSTGRES_RO_USER:
        user = settings.POSTGRES_RO_USER
        password = settings.POSTGRES_RO_PASSWORD or settings.POSTGRES_PASSWORD
    return psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=user,
        password=password,
        client_encoding="utf8",
    )


def ping_database() -> tuple[bool, int | None]:
    try:
        row = run_scalar_query("SELECT COUNT(*) FROM fact_ventas")
        return True, int(row[0]) if row else 0
    except Exception:
        return False, None


def _json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def run_parameterized_select(sql: str, params: tuple = ()) -> list[dict]:
    """SELECT interno con parámetros (no expuesto al LLM)."""
    conn = _connect(readonly=True)
    try:
        cur = conn.cursor()
        try:
            cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
            cur.execute(sql, params)
            columns = [desc[0] for desc in cur.description or []]
            rows = cur.fetchall()
        finally:
            cur.close()
        return [
            {columns[i]: _json_safe(row[i]) for i in range(len(columns))}
            for row in rows
        ]
    finally:
        conn.close()


def run_scalar_query(sql: str, params: tuple = ()) -> tuple | None:
    rows = run_parameterized_select(sql, params)
    if not rows:
        return None
    first = rows[0]
    return tuple(first.values())


def run_validated_select(validated_sql: str):
    """Ejecuta un SELECT ya validado. Preferir usuario read-only si está configurado."""
    conn = _connect(readonly=True)
    try:
        cur = conn.cursor()
        try:
            cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
            cur.execute(validated_sql)
            columns = [desc[0] for desc in cur.description or []]
            rows = cur.fetchall()
        finally:
            cur.close()
        return [
            {columns[i]: _json_safe(row[i]) for i in range(len(columns))}
            for row in rows
        ]
    finally:
        conn.close()
