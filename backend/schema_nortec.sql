-- Nortec star schema (retail electrónica Latam)
DROP VIEW IF EXISTS v_ventas_linea CASCADE;
DROP TABLE IF EXISTS fact_ventas CASCADE;
DROP TABLE IF EXISTS dim_sucursal CASCADE;
DROP TABLE IF EXISTS dim_cliente CASCADE;
DROP TABLE IF EXISTS dim_producto CASCADE;
DROP TABLE IF EXISTS dim_tiempo CASCADE;
DROP TABLE IF EXISTS ventas CASCADE;

CREATE TABLE dim_tiempo (
    fecha DATE PRIMARY KEY,
    mes SMALLINT NOT NULL,
    trimestre SMALLINT NOT NULL,
    anio SMALLINT NOT NULL,
    es_fin_de_semana BOOLEAN NOT NULL
);

CREATE TABLE dim_producto (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(32) NOT NULL UNIQUE,
    nombre VARCHAR(120) NOT NULL,
    categoria VARCHAR(60) NOT NULL,
    subcategoria VARCHAR(60) NOT NULL,
    marca VARCHAR(60) NOT NULL,
    costo NUMERIC(12, 2) NOT NULL,
    precio_lista NUMERIC(12, 2) NOT NULL
);

CREATE TABLE dim_cliente (
    id SERIAL PRIMARY KEY,
    segmento VARCHAR(20) NOT NULL,
    ciudad VARCHAR(80) NOT NULL,
    provincia VARCHAR(80) NOT NULL
);

CREATE TABLE dim_sucursal (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    region VARCHAR(40) NOT NULL,
    canal VARCHAR(20) NOT NULL
);

CREATE TABLE fact_ventas (
    id BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL REFERENCES dim_tiempo (fecha),
    producto_id INTEGER NOT NULL REFERENCES dim_producto (id),
    cliente_id INTEGER NOT NULL REFERENCES dim_cliente (id),
    sucursal_id INTEGER NOT NULL REFERENCES dim_sucursal (id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12, 2) NOT NULL,
    descuento_pct NUMERIC(5, 2) NOT NULL DEFAULT 0,
    costo_unitario NUMERIC(12, 2) NOT NULL
);

CREATE INDEX idx_fact_ventas_fecha ON fact_ventas (fecha);
CREATE INDEX idx_fact_ventas_producto ON fact_ventas (producto_id);
CREATE INDEX idx_fact_ventas_sucursal ON fact_ventas (sucursal_id);

CREATE VIEW v_ventas_linea AS
SELECT
    f.id AS linea_id,
    t.fecha,
    t.mes,
    t.trimestre,
    t.anio,
    t.es_fin_de_semana,
    p.sku,
    p.nombre AS producto,
    p.categoria,
    p.subcategoria,
    p.marca,
    c.segmento,
    c.ciudad,
    c.provincia,
    s.nombre AS sucursal,
    s.region,
    s.canal,
    f.cantidad,
    f.precio_unitario,
    f.descuento_pct,
    f.costo_unitario,
    ROUND(
        (f.cantidad * f.precio_unitario * (1 - f.descuento_pct / 100.0))::numeric,
        2
    ) AS ingresos,
    ROUND(
        (
            f.cantidad * f.precio_unitario * (1 - f.descuento_pct / 100.0)
            - f.cantidad * f.costo_unitario
        )::numeric,
        2
    ) AS margen
FROM fact_ventas f
JOIN dim_tiempo t ON f.fecha = t.fecha
JOIN dim_producto p ON f.producto_id = p.id
JOIN dim_cliente c ON f.cliente_id = c.id
JOIN dim_sucursal s ON f.sucursal_id = s.id;

DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'insight_ai_ro') THEN
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO insight_ai_ro;
    GRANT SELECT ON v_ventas_linea TO insight_ai_ro;
  END IF;
END
$$;
