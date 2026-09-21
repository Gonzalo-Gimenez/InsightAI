-- Legacy: el warehouse Nortec se carga con el generador Python.
-- Desde backend/ con venv activado:
--   python -m scripts.seed_nortec
-- Opciones: --rows 190000 (default, mar 2024–sep 2026) | --rows 5000 (rápido para pruebas)

SELECT 'Use: python -m scripts.seed_nortec' AS instruccion;
