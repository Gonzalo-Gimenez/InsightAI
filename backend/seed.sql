-- Idempotent demo seed (safe for managed Postgres; no psql meta-commands)
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    producto VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    ventas INTEGER NOT NULL DEFAULT 0,
    fecha DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE ventas ADD COLUMN IF NOT EXISTS fecha DATE;

INSERT INTO ventas (producto, categoria, region, ventas, fecha) VALUES
    ('Laptop', 'Electrónica', 'Norte', 1500, '2026-01-15'),
    ('Mouse', 'Accesorios', 'Sur', 120, '2026-01-18'),
    ('Teclado', 'Accesorios', 'Norte', 80, '2026-01-20'),
    ('Monitor', 'Electrónica', 'Sur', 300, '2026-02-03'),
    ('Impresora', 'Oficina', 'Norte', 200, '2026-02-08'),
    ('Webcam HD', 'Accesorios', 'Sur', 95, '2026-02-12'),
    ('Router WiFi', 'Electrónica', 'Norte', 210, '2026-02-14'),
    ('Silla ergonómica', 'Oficina', 'Sur', 160, '2026-02-20'),
    ('Auriculares', 'Accesorios', 'Norte', 140, '2026-03-01'),
    ('Tablet 10"', 'Electrónica', 'Sur', 420, '2026-03-05'),
    ('Dock USB-C', 'Accesorios', 'Norte', 75, '2026-03-08'),
    ('Proyector', 'Electrónica', 'Sur', 380, '2026-03-10')
ON CONFLICT (producto) DO NOTHING;
