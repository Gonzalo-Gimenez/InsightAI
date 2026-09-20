-- Idempotent demo seed (safe for managed Postgres; no psql meta-commands)
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    producto VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    ventas INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO ventas (producto, categoria, region, ventas) VALUES
    ('Laptop', 'Electrónica', 'Norte', 1500),
    ('Mouse', 'Accesorios', 'Sur', 120),
    ('Teclado', 'Accesorios', 'Norte', 80),
    ('Monitor', 'Electrónica', 'Sur', 300),
    ('Impresora', 'Oficina', 'Norte', 200)
ON CONFLICT DO NOTHING;
