# TaskBoard

TaskBoard is a small project-management application used as a DevOps capstone. A React UI talks to a FastAPI service, PostgreSQL stores the tasks, and the same application is packaged for Docker, GitHub Actions, Terraform, Helm, Argo CD, and Prometheus.

## Architecture

```text
Browser
  |
  |  http://localhost:3000
  v
Nginx (frontend image)
  |  /            static React app
  |  /api/*       proxy
  v
FastAPI (backend image) ---- PostgreSQL
  |
  |  /metrics
  v
Prometheus --> Grafana
```

The browser never needs the backend hostname. Nginx proxies `/api` in Docker Compose. Kubernetes Ingress does the same split: `/` to the frontend Service and `/api` to the backend Service. A fuller diagram is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Stack

- Frontend: React 18, Vite 6, Nginx
- Backend: Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic, Pytest
- Database: PostgreSQL 16
- Containers: Docker Compose
- CI: GitHub Actions, Trivy, GHCR
- Infrastructure: Terraform, AWS VPC and EKS 1.35 in `ap-southeast-2`
- Runtime: Helm, Kubernetes Ingress, HPA, Argo CD
- Monitoring: Prometheus scrape of `/metrics`, Grafana dashboard

## Features

- Create, list, read, update, and delete tasks
- Status values `TODO`, `IN_PROGRESS`, and `DONE`
- Priority values `LOW`, `MEDIUM`, and `HIGH`
- `GET /api/stats` and `GET /api/tasks/stats`
- Liveness `GET /health`, readiness `GET /ready` (runs `SELECT 1`)
- Prometheus metrics on `GET /metrics`
- Alembic migration `0001_create_tasks` is the schema path. The API process does not call `create_all`.

## Prerequisites

- Docker Engine and Docker Compose v2
- Python 3.12 and Node.js 22 if you run the apps outside containers
- Terraform >= 1.7 and AWS credentials only when you plan or apply infrastructure
- kubectl, Helm, and an ingress controller only when you install the chart

## Local setup

```bash
cp .env.example .env
# Edit .env and replace every password placeholder.

docker compose up --build
```

- UI: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

Stop and keep the database volume:

```bash
docker compose down
```

Stop and delete the database volume:

```bash
docker compose down -v
```

Optional Prometheus and Grafana (still local, not a cluster):

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml --profile observability up --build
```

Grafana listens on port 3001. Anonymous viewers can open the TaskBoard dashboard. The admin password comes from `GRAFANA_ADMIN_PASSWORD`.

### Run the API on the host

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://taskboard:replace-with-a-long-random-password@localhost:5432/taskboard'
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

For a password-free smoke test, point `DATABASE_URL` at a SQLite file and run `alembic upgrade head` before Uvicorn. Tests use an in-memory SQLite database and create tables only in the test fixture.

### Frontend dev server

```bash
cd frontend
npm ci
npm test
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`.

## Environment

Copy [.env.example](.env.example). Placeholders only. `.env` is gitignored. Compose refuses to start until `POSTGRES_PASSWORD` is set. Do not reuse the placeholder as a real password.

| Variable | Purpose |
| --- | --- |
| `POSTGRES_USER` | Database role. `taskboard` is the role name, not a password. |
| `POSTGRES_PASSWORD` | Database password. Required. |
| `POSTGRES_DB` | Database name. |
| `BACKEND_PORT` / `FRONTEND_PORT` | Host ports. Defaults 8000 and 3000. |
| `GRAFANA_ADMIN_PASSWORD` | Required only for the observability Compose file. |

Kubernetes does not read this file. Create a Secret named `taskboard-db` with keys `username`, `password`, and `database`. The chart builds `DATABASE_URL` from that Secret and the Postgres Service hostname.

## Tests

```bash
cd backend
pytest -q
```

The suite covers health, readiness, a database-down readiness failure, create, list, get, update, delete, validation, stats, filters, metrics, and Alembic upgrade/downgrade. It does not use the Compose database.

```bash
cd frontend
npm test
npm run build
```

## CI/CD and GHCR

[`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) runs on pull requests and on pushes to `main`.

- Every pull request and every main push: pytest, frontend test and build, Compose config, image build, Trivy.
- Pull requests do not receive `packages: write` and do not log in to GHCR.
- Pushes to `main` publish immutable images:

```text
ghcr.io/<owner>/<repo>/backend:<git-sha>
ghcr.io/<owner>/<repo>/frontend:<git-sha>
```

`<owner>/<repo>` is `github.repository`, lowercased. There is no `latest` tag.

After a publish, the `gitops` job writes the new SHA into `helm/taskboard/values-eks.yaml` and commits it as `github-actions[bot]` with `[skip ci]`. Argo CD watches that file, so a push to `main` is a deploy:

```text
git push → pytest + build → Trivy → GHCR :<sha> → bot commit to values-eks.yaml → Argo CD sync → new pods
```

## Terraform

`terraform/` describes a VPC (two public and two private subnets, one NAT gateway) and an EKS 1.35 cluster in `ap-southeast-2` with one managed node group (2 × `m7i-flex.large`, Amazon Linux 2023) and the EBS CSI add-on. The plan creates 59 resources.

The numbered scripts in [`scripts/aws/`](scripts/aws) run each stage and log to `logs/`:

| Script | What it does |
| --- | --- |
| `00-install-tools.sh` | Homebrew install of awscli, terraform, kubectl, helm |
| `01-aws-check.sh` | `aws sts get-caller-identity` and available EKS versions |
| `02-terraform-plan.sh` / `03-terraform-apply.sh` | init, validate, plan, apply, kubeconfig |
| `04-cluster-addons.sh` | gp3 StorageClass, ingress-nginx on an NLB, Metrics Server |
| `05-monitoring.sh` | kube-prometheus-stack (must precede the app: the chart has a ServiceMonitor) |
| `06-deploy-app.sh` | DB secret, `helm upgrade --install`, smoke test through the Ingress |
| `07-argocd.sh` | Argo CD and the `taskboard` Application |
| `08-open-dashboards.sh` | port-forwards for Argo CD, Prometheus, Grafana |
| `09-load-test.sh` | traffic for the dashboards and HPA |
| `99-destroy.sh` | removes load balancer and volumes, then `terraform destroy` |

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
aws eks update-kubeconfig --region ap-southeast-2 --name taskboard-eks
```

Destroy when you are done. Cost notes are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Helm and Argo CD

```bash
kubectl apply -f k8s/namespace.yaml
kubectl -n taskboard create secret generic taskboard-db \
  --from-literal=username=taskboard \
  --from-literal=password='REPLACE_WITH_A_LONG_RANDOM_PASSWORD' \
  --from-literal=database=taskboard

helm upgrade --install taskboard ./helm/taskboard \
  --namespace taskboard \
  -f helm/taskboard/values-eks.yaml
```

The chart ships Deployments, ClusterIP Services, a Postgres PVC, probes, resource requests and limits, an Ingress, a backend HPA, a ServiceMonitor, and a Grafana dashboard ConfigMap. Broken classroom manifests live only under `troubleshooting/` and use the namespace `taskboard-troubleshoot`.

`gitops/argocd/application.yaml` is the Argo CD Application. It tracks `helm/taskboard` on `main` with `values.yaml` and `values-eks.yaml`, with automated sync, prune, and self-heal. Helm performs the first install; Argo CD keeps the release equal to git afterwards.

## Monitoring

`GET /metrics` exposes `http_requests_total`, `http_request_duration_seconds`, `taskboard_tasks_created_total`, `taskboard_tasks_updated_total`, `taskboard_tasks_deleted_total`, and `taskboard_tasks_by_status`. The Grafana dashboard queries those names. See [docs/MONITORING.md](docs/MONITORING.md).

## Troubleshooting

[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) lists symptoms, commands, causes, and fixes, including the disposable ImagePullBackOff and Service-selector exercise.

## Security

No production password is committed. Images run the API as uid 10001 and Nginx as uid 101. The Postgres server process runs as uid 70. Trivy fails the pipeline on HIGH and CRITICAL findings. Details and the local scan result are in [docs/SECURITY.md](docs/SECURITY.md).

## Cleanup and cost

An EKS control plane is billed per hour (the public rate is $0.10 per hour in standard support). A NAT gateway is billed per hour plus data processing. Two `m7i-flex.large` nodes and the NLB add compute, EBS, and load balancer charges. In `ap-southeast-2` the whole stack is roughly $0.40 per hour. Delete the Helm release and run `terraform destroy` when the demo ends. Commands are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Known issues and limitations

- **Region is fixed to `ap-southeast-2`.** The AWS account sits in an AWS Organization whose SCP denies EC2 and EKS in every other region.
- **No IRSA.** The same SCP denies `iam:CreateOpenIDConnectProvider`, so `enable_irsa = false`. The EBS CSI driver uses the node role (`AmazonEBSCSIDriverPolicy`) instead of a pod-scoped role.
- **Node type is `m7i-flex.large`.** The account is on the AWS Free plan, which only launches free-tier-eligible types; `t3.medium` is rejected.
- **ingress-nginx** is used for the classroom Ingress. The upstream project is in maintenance-only mode; a production setup would use the AWS Load Balancer Controller.
- **Postgres runs in the cluster** on a single gp3 PVC. Production would use Amazon RDS.
- **The Ingress has no host rule**, so the app answers on the NLB hostname over plain HTTP. There is no TLS or DNS name.

## Links

- [Architecture](docs/ARCHITECTURE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Security](docs/SECURITY.md)
- [Monitoring](docs/MONITORING.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Demo script](docs/DEMO_SCRIPT.md)
- [Rubric mapping](docs/RUBRIC_MAPPING.md)
- [Slides](docs/presentation/01-overview.md)
- [Shot list](demo/DEMO_SCRIPT.md)
- [Implementation status](IMPLEMENTATION_STATUS.md)
