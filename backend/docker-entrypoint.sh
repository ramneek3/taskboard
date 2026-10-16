#!/bin/sh
set -eu

if [ -z "${DATABASE_URL:-}" ]; then
  if [ -z "${POSTGRES_PASSWORD:-}" ] || [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_DB:-}" ]; then
    echo "Set DATABASE_URL, or POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB." >&2
    exit 1
  fi
  DATABASE_URL="$(python - <<'PY'
import os
from urllib.parse import quote

user = quote(os.environ["POSTGRES_USER"], safe="")
password = quote(os.environ["POSTGRES_PASSWORD"], safe="")
database = quote(os.environ["POSTGRES_DB"], safe="")
host = os.environ.get("POSTGRES_HOST", "postgres")
port = os.environ.get("POSTGRES_PORT", "5432")
print(f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}")
PY
)"
  export DATABASE_URL
fi

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
