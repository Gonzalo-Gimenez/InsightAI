import re

_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|"
    r"EXECUTE|COPY|INTO|UNION|INTERSECT|EXCEPT|;\s*\S)\b",
    re.IGNORECASE,
)

_ALLOWED_TABLES = {
    "dim_tiempo",
    "dim_producto",
    "dim_cliente",
    "dim_sucursal",
    "fact_ventas",
    "v_ventas_linea",
}

_FORBIDDEN_TABLES = {"pg_catalog", "information_schema"}

_MAX_LIMIT = 100


def _extract_tables(cleaned: str) -> list[str]:
    lowered = cleaned.lower()
    tables = re.findall(r"\bfrom\s+([a-z_][a-z0-9_]*)", lowered)
    tables += re.findall(r"\bjoin\s+([a-z_][a-z0-9_]*)", lowered)
    return tables


def validate_readonly_select(sql: str) -> str:
    """Valida un único SELECT de solo lectura sobre tablas permitidas."""
    cleaned = sql.strip().rstrip(";").strip()
    if not cleaned:
        raise ValueError("La consulta SQL está vacía")

    if ";" in cleaned:
        raise ValueError("Solo se permite un statement SQL")

    if _FORBIDDEN.search(cleaned):
        raise ValueError("La consulta contiene operaciones no permitidas")

    if not re.match(r"^SELECT\b", cleaned, re.IGNORECASE):
        raise ValueError("Solo se permiten consultas SELECT")

    lowered = cleaned.lower()
    if not re.search(r"\bfrom\b", lowered):
        raise ValueError("La consulta debe incluir FROM")

    for table in _extract_tables(cleaned):
        if table in _FORBIDDEN_TABLES:
            raise ValueError(f"Tabla no permitida: {table}")
        if table not in _ALLOWED_TABLES:
            raise ValueError(f"Tabla no permitida: {table}")

    if re.search(r"\blimit\s+(\d+)", lowered):
        match = re.search(r"\blimit\s+(\d+)", lowered)
        if match and int(match.group(1)) > _MAX_LIMIT:
            raise ValueError(f"LIMIT máximo permitido: {_MAX_LIMIT}")
    else:
        cleaned = f"{cleaned} LIMIT {_MAX_LIMIT}"

    return cleaned
