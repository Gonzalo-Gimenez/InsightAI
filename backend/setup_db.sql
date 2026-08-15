-- PostgreSQL setup script for InsightAI
-- Run this script after starting PostgreSQL

-- Create the database (if not exists)
-- CREATE DATABASE insight_ai;

-- Connect to the database
\c insight_ai;

-- Create the ventas table
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    producto VARCHAR(100) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    ventas INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data equivalent to the original data_analysis sample
INSERT INTO ventas (producto, categoria, region, ventas) VALUES
    ('Laptop', 'Electrónica', 'Norte', 1500),
    ('Mouse', 'Accesorios', 'Sur', 120),
    ('Teclado', 'Accesorios', 'Norte', 80),
    ('Monitor', 'Electrónica', 'Sur', 300),
    ('Impresora', 'Oficina', 'Norte', 200)
ON CONFLICT DO NOTHING;

-- Verify inserted data
SELECT * FROM ventas;