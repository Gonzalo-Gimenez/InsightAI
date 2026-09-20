#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  echo "Applying demo seed (idempotent)..."
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f /app/seed.sql || true
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
