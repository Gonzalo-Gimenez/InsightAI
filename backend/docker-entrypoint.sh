#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  echo "Checking Nortec warehouse..."
  need_seed="$(python - <<'PY'
from datetime import date

from app.services.ventas_db import ping_database

ok, n = ping_database()
need = True
if ok and n and n >= 1000:
    try:
        from app.services.nortec_analytics import date_bounds

        _, hasta = date_bounds()
        need = hasta < date(2026, 9, 1)
    except Exception:
        need = True
print("1" if need else "0")
PY
)"
  if [ "$need_seed" = "1" ]; then
    echo "Seeding Nortec (idempotent recreate)..."
    python -m scripts.seed_nortec --rows 80000
  else
    echo "Nortec already loaded, skip seed."
  fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
