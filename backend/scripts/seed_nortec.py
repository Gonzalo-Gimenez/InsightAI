#!/usr/bin/env python3
"""Genera el dataset Nortec (~190k líneas de fact_ventas) de forma determinista."""

import argparse
import calendar
import random
from datetime import date, timedelta
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch

from app.config import settings

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema_nortec.sql"

CATEGORIAS = {
    "Notebooks": ("Laptops", "Ultrabooks"),
    "Periféricos": ("Teclados", "Mouse", "Webcams"),
    "Monitores": ("Gaming", "Oficina"),
    "Audio": ("Auriculares", "Parlantes"),
    "Redes": ("Routers", "Switches"),
    "Almacenamiento": ("SSD", "HDD externos"),
    "Smartphones": ("Gama media", "Gama alta"),
    "Tablets": ("10 pulgadas", "Pro"),
}

MARCAS = [
    "Nortec",
    "Aster",
    "Volt",
    "Lumen",
    "Kairo",
    "Pulse",
    "Orbit",
]

REGIONES = ["Norte", "Cuyo", "Litoral", "AMBA", "Patagonia"]
SUCURSALES = [
    ("Centro Córdoba", "Cuyo", "tienda"),
    ("Rosario Norte", "Litoral", "tienda"),
    ("Mendoza Plaza", "Cuyo", "tienda"),
    ("Salta Centro", "Norte", "tienda"),
    ("Palermo", "AMBA", "tienda"),
    ("Belgrano", "AMBA", "tienda"),
    ("La Plata", "AMBA", "tienda"),
    ("Neuquén", "Patagonia", "tienda"),
    ("Tucumán", "Norte", "tienda"),
    ("Mar del Plata", "Litoral", "tienda"),
    ("Tienda Online AR", "AMBA", "online"),
    ("Outlet Online", "AMBA", "online"),
]

CIUDADES = [
    ("Córdoba", "Córdoba"),
    ("Rosario", "Santa Fe"),
    ("Mendoza", "Mendoza"),
    ("Salta", "Salta"),
    ("Buenos Aires", "CABA"),
    ("La Plata", "Buenos Aires"),
    ("Neuquén", "Neuquén"),
    ("Tucumán", "Tucumán"),
    ("Mar del Plata", "Buenos Aires"),
    ("Resistencia", "Chaco"),
]

START = date(2024, 3, 1)
END = date(2026, 9, 30)


def _connect():
    return psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        client_encoding="utf8",
    )


def _daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _load_schema(cur):
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    cur.execute(sql)


def _seed_tiempo(cur, rng: random.Random):
    rows = []
    for d in _daterange(START, END):
        rows.append(
            (
                d,
                d.month,
                (d.month - 1) // 3 + 1,
                d.year,
                d.weekday() >= 5,
            )
        )
    execute_batch(
        cur,
        """
        INSERT INTO dim_tiempo (fecha, mes, trimestre, anio, es_fin_de_semana)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (fecha) DO NOTHING
        """,
        rows,
        page_size=500,
    )


def _seed_productos(cur, rng: random.Random, count: int = 180):
    productos = []
    sku_i = 1
    for cat, subs in CATEGORIAS.items():
        for sub in subs:
            for _ in range(max(8, count // (len(CATEGORIAS) * 2))):
                if sku_i > count:
                    break
                marca = rng.choice(MARCAS)
                costo = round(rng.uniform(80, 2500), 2)
                precio = round(costo * rng.uniform(1.25, 1.65), 2)
                productos.append(
                    (
                        f"NT-{sku_i:04d}",
                        f"{marca} {sub} {sku_i}",
                        cat,
                        sub,
                        marca,
                        costo,
                        precio,
                    )
                )
                sku_i += 1
    execute_batch(
        cur,
        """
        INSERT INTO dim_producto (sku, nombre, categoria, subcategoria, marca, costo, precio_lista)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        productos[:count],
        page_size=200,
    )


def _seed_clientes(cur, rng: random.Random, count: int = 8000):
    rows = []
    for i in range(count):
        ciudad, provincia = rng.choice(CIUDADES)
        segmento = "pyme" if rng.random() < 0.22 else "consumer"
        rows.append((segmento, ciudad, provincia))
    execute_batch(
        cur,
        """
        INSERT INTO dim_cliente (segmento, ciudad, provincia) VALUES (%s, %s, %s)
        """,
        rows,
        page_size=500,
    )


def _seed_sucursales(cur):
    execute_batch(
        cur,
        """
        INSERT INTO dim_sucursal (nombre, region, canal) VALUES (%s, %s, %s)
        """,
        SUCURSALES,
    )


def _product_weights(cur, rng: random.Random) -> list[tuple[int, float]]:
    cur.execute("SELECT id, categoria, precio_lista FROM dim_producto")
    rows = cur.fetchall()
    weights = []
    for pid, categoria, precio in rows:
        base = 1.0
        if categoria in ("Notebooks", "Smartphones"):
            base = 2.8
        elif categoria == "Periféricos":
            base = 1.6
        if float(precio) > 1500:
            base *= 0.7
        weights.append((pid, base))
    return weights


def _seed_facts(cur, rng: random.Random, target_rows: int):
    cur.execute("SELECT id FROM dim_cliente")
    clientes = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id, canal FROM dim_sucursal")
    sucursales = cur.fetchall()
    online_ids = [s[0] for s in sucursales if s[1] == "online"]
    tienda_ids = [s[0] for s in sucursales if s[1] == "tienda"]

    product_weights = _product_weights(cur, rng)
    product_ids = [p[0] for p in product_weights]
    probs = [p[1] for p in product_weights]
    total_w = sum(probs)
    norm = [w / total_w for w in probs]

    cur.execute(
        "SELECT id, costo, precio_lista FROM dim_producto"
    )
    prod_map = {r[0]: (float(r[1]), float(r[2])) for r in cur.fetchall()}

    days = list(_daterange(START, END))
    rows_per_day = max(1, target_rows // len(days))
    batch = []
    inserted = 0

    for d in days:
        seasonal = 1.0
        if d.month in (11, 12):
            seasonal = 1.35
        elif d.month in (6, 7):
            seasonal = 0.85
        day_count = int(rows_per_day * seasonal * rng.uniform(0.85, 1.15))
        day_count = max(1, min(day_count, 400))

        for _ in range(day_count):
            pid = rng.choices(product_ids, weights=norm, k=1)[0]
            costo, lista = prod_map[pid]
            cliente = rng.choice(clientes)
            if rng.random() < 0.38:
                sucursal = rng.choice(online_ids)
            else:
                sucursal = rng.choice(tienda_ids)
            cantidad = rng.choices([1, 2, 3, 4, 5], weights=[70, 18, 7, 3, 2], k=1)[0]
            descuento = round(rng.uniform(0, 18) if rng.random() < 0.4 else 0, 2)
            precio = round(lista * rng.uniform(0.92, 1.05), 2)
            batch.append(
                (
                    d,
                    pid,
                    cliente,
                    sucursal,
                    cantidad,
                    precio,
                    descuento,
                    costo,
                )
            )
            inserted += 1
            if len(batch) >= 2000:
                execute_batch(
                    cur,
                    """
                    INSERT INTO fact_ventas (
                        fecha, producto_id, cliente_id, sucursal_id,
                        cantidad, precio_unitario, descuento_pct, costo_unitario
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    batch,
                    page_size=1000,
                )
                batch.clear()

    if batch:
        execute_batch(
            cur,
            """
            INSERT INTO fact_ventas (
                fecha, producto_id, cliente_id, sucursal_id,
                cantidad, precio_unitario, descuento_pct, costo_unitario
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            batch,
            page_size=1000,
        )


def run(target_rows: int = 190_000, seed: int = 42):
    rng = random.Random(seed)
    conn = _connect()
    try:
        conn.autocommit = False
        cur = conn.cursor()
        _load_schema(cur)
        _seed_tiempo(cur, rng)
        _seed_productos(cur, rng)
        _seed_clientes(cur, rng)
        _seed_sucursales(cur)
        _seed_facts(cur, rng, target_rows)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM fact_ventas")
        count = cur.fetchone()[0]
        print(f"Nortec seed OK: {count} filas en fact_ventas")
        cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed Nortec warehouse")
    parser.add_argument(
        "--rows",
        type=int,
        default=190_000,
        help="Filas objetivo en fact_ventas (default 190000)",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run(target_rows=args.rows, seed=args.seed)


if __name__ == "__main__":
    main()
