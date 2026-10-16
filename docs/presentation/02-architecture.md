# Architecture

```text
Browser -> Nginx or Ingress
              |-- /      React
              |-- /api   FastAPI -> PostgreSQL
FastAPI /metrics -> Prometheus -> Grafana
```

## Why the browser does not know the API host

Compose puts Nginx and the API on one network. Nginx proxies `/api` to `backend:8000`. In the cluster, Ingress sends `/api` to the backend Service and `/` to the frontend Service. The Helm chart sets `BACKEND_UPSTREAM` so the same Nginx image still proxies if traffic reaches it directly.

## Schema

Alembic revision `0001_create_tasks` creates `tasks` and `ix_tasks_status`. Uvicorn does not call `create_all`.
