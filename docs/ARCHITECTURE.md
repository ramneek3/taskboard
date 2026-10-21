# Architecture

TaskBoard is one application with two deployable processes and one database. The production schema is applied by Alembic before Uvicorn starts. The API process does not create tables.

```mermaid
flowchart LR
  user[Browser]
  subgraph compose [Docker Compose network taskboard]
    nginx[Nginx frontend]
    api[FastAPI backend]
    db[(PostgreSQL)]
  end
  user -->|GET /| nginx
  user -->|/api/*| nginx
  nginx -->|proxy_pass| api
  api -->|SQLAlchemy| db
  api -->|GET /metrics| prom[Prometheus]
  prom --> graf[Grafana]
```

On Kubernetes the same split is an Ingress, not an in-cluster dependency on the Compose DNS name `backend`.

```mermaid
flowchart TB
  dev[Git commit] --> gha[GitHub Actions]
  gha --> test[pytest and frontend build]
  test --> images[Image build]
  images --> trivy[Trivy HIGH and CRITICAL]
  trivy --> ghcr[GHCR sha tags]
  ghcr --> argo[Argo CD Application]
  tf[Terraform VPC and EKS] --> cluster[EKS ap-southeast-2]
  argo --> helm[Helm release]
  helm --> cluster
  subgraph ns [namespace taskboard]
    ing[Ingress]
    fe[frontend Deployment]
    be[backend Deployment]
    pg[Postgres plus PVC]
    hpa[HPA]
    sm[ServiceMonitor]
  end
  cluster --> ns
  ing -->|/| fe
  ing -->|/api| be
  be --> pg
  sm --> be
```

## Request path

| Caller | Path | Process |
| --- | --- | --- |
| Browser | `/` | Nginx serves the Vite build |
| Browser | `/api/tasks`, `/api/stats` | Nginx or Ingress forwards to FastAPI |
| Kubernetes | `/health` | Liveness, no database call |
| Kubernetes | `/ready` | Readiness, `SELECT 1` |
| Prometheus | `/metrics` | FastAPI instrumentator plus TaskBoard counters |

## Data

Table `tasks` is created by revision `0001_create_tasks`. Columns: `id`, `title`, `description`, `priority`, `status`, `assignee`, `created_at`. Index `ix_tasks_status` supports the stats query.

## What is intentionally outside the healthy release

`troubleshooting/broken-image.yaml` and `troubleshooting/broken-service.yaml` target namespace `taskboard-troubleshoot`. Helm does not render them.
