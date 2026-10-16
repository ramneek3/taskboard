# Implementation status

This file is the evidence log for the TaskBoard capstone. Commands were run in this workspace on 16 October 2026. Results below are from those commands.

## What was implemented

- FastAPI task API with `/`, `/health`, `/ready`, `/metrics`, task CRUD, `/api/stats`, and `/api/tasks/stats`
- Alembic revision `0001_create_tasks` as the only schema path. The API does not call `create_all`
- React + Vite UI served by Nginx, proxying `/api`
- Docker Compose for frontend, backend, and Postgres, plus an optional Prometheus and Grafana profile
- GitHub Actions: tests and image builds on pull requests, Trivy gate, GHCR publish of SHA tags only on push to `main`
- Terraform VPC and EKS in `ap-south-1`, Kubernetes 1.35. Not applied
- Helm chart with Deployments, Services, Postgres PVC, probes, resources, Ingress, HPA, ServiceMonitor, Grafana dashboard ConfigMap
- Argo CD Application manifest. Not applied
- Troubleshooting manifests limited to namespace `taskboard-troubleshoot`
- Docs, eight slides, and a demo shot list. No video

## Verification

| Check | Command | Result |
| --- | --- | --- |
| Backend tests | `cd backend && .venv/bin/pytest -q` | PASS. 13 passed |
| Alembic on SQLite | `DATABASE_URL=sqlite:////tmp/taskboard-smoke.db alembic upgrade head` then `alembic current` | PASS. `0001_create_tasks (head)` |
| Frontend tests | `cd frontend && npm test` | PASS. 4 passed |
| Frontend production build | `cd frontend && npm run build` | PASS. Vite wrote `dist/` |
| Compose config | `POSTGRES_PASSWORD` set in the shell, then `docker compose config` | PASS |
| Observability Compose config | same, plus `GRAFANA_ADMIN_PASSWORD` set in the shell and `--profile observability` | PASS |
| Workflow YAML | `actionlint .github/workflows/ci-cd.yml` | PASS |
| Helm | `helm lint helm/taskboard` and `helm template taskboard helm/taskboard -n taskboard` | PASS. Lint reported only that an icon is recommended |
| Rendered manifests | `kubeconform -kubernetes-version 1.35.0` plus the datreeio CRD catalog | PASS. 11 valid, 0 invalid |
| Terraform format | `terraform -chdir=terraform fmt -recursive` | PASS |
| Terraform init | `terraform -chdir=terraform init -backend=false -input=false` | PASS. Providers and modules downloaded |
| Terraform validate | `terraform -chdir=terraform validate` | PASS. `Success! The configuration is valid.` |
| Terraform plan | `terraform -chdir=terraform plan -input=false` | BLOCKED. Exit 1. `No valid credential sources found` |
| Terraform apply | not run | NOT RUN |
| Image build | `docker compose build` | PASS. Backend and frontend images built |
| Trivy images | `trivy image --severity HIGH,CRITICAL --exit-code 1 taskboard-backend:latest` and the frontend image | PASS. Exit 0. No HIGH or CRITICAL findings after the Alpine rebuild |
| Compose up | `docker compose up -d` | PASS. postgres, backend, and frontend reported healthy |
| CRUD through Nginx | `POST/PUT/DELETE http://127.0.0.1:3000/api/tasks` and `GET /api/stats` | PASS. Create 201, update 200, delete 204, missing id 404 |
| Non-root | `docker exec` id and `docker top` | PASS. API uid 10001, Nginx uid 101, Postgres server uid 70 |
| Prometheus | `curl http://127.0.0.1:9090/api/v1/targets` | PASS. Target `taskboard-backend` health `up` at `http://backend:8000/metrics` |
| Prometheus query | `sum(taskboard_tasks_by_status)` | PASS. Returned value `1` while one task was stored |
| Grafana | `curl http://127.0.0.1:3001/api/health` and `/api/search` | PASS. Health 200. Dashboard `TaskBoard API` uid `taskboard-api` provisioned |
| GitHub Actions run | not run | NOT RUN |
| GHCR publish | not run | NOT RUN |
| Argo CD | not installed | NOT RUN |
| EKS / kubectl | no cluster | NOT RUN |

The first image scan, before the base images were switched to Alpine and upgraded, reported HIGH findings (Starlette on the old pin, and Alpine/Debian packages). The Dockerfiles now use `python:3.12-alpine` and `nginxinc/nginx-unprivileged` with `apk upgrade`, and the API pins FastAPI 0.143.2, Starlette 1.8.0, and prometheus-fastapi-instrumentator 8.1.0. The rescan above is the one that counts.

## Was the app run?

Yes. The Compose stack served the UI on port 3000 and the API on port 8000. A task was created through the Nginx `/api` proxy and stored in Postgres (`alembic_version` and `tasks` both exist). Prometheus scraped `/metrics`. Grafana loaded the dashboard. That is local Docker, not AWS.

## AWS / EKS

Not applied. No cluster, VPC, or NAT gateway was created. `terraform plan` did not refresh AWS because no credentials were available.

## GitHub Actions and GHCR

Actions run [38859671050](https://github.com/ramneek3/taskboard/actions/runs/38859671050) on `d5f4f6c` succeeded for Helm lint and template, Terraform validate, Test and build frontend, and Build images and Trivy gate.

Publish on `d5f4f6c` (run 38859671050) failed pushing `ghcr.io/ramneek3/taskboard-backend:<sha>` with `denied: permission_denied: write_package`. `GITHUB_TOKEN` cannot create a package whose name is not the repository. The label-only commit `e90e9c0` (run 38861380362) was cancelled by `concurrency.cancel-in-progress` before publish ran. Images are now `ghcr.io/<owner>/<repo>/backend` and `ghcr.io/<owner>/<repo>/frontend`, tagged only with the commit SHA. This file does not claim that publish succeeded.

## Argo CD, Prometheus, Grafana

- Argo CD: not installed. The Application manifest is only a file. No sync status.
- Prometheus and Grafana: ran locally via Compose. They did not run inside Kubernetes. The ServiceMonitor was validated as YAML by kubeconform. It was not scraped by a Prometheus Operator.

## Rubric

| Category | State |
| --- | --- |
| App | Complete and run locally |
| Tests | Complete. 13 backend tests passed |
| Git/GitHub | Files and ignore rules are here. Remote publish is the push recorded at the bottom of this file after it succeeds |
| Docker/Compose | Complete. Built and run |
| GitHub Actions | Live run on `d5f4f6c` passed tests, Trivy, Terraform, and Helm. Publish failed with `write_package`. Images now use `ghcr.io/<owner>/<repo>/backend` and `.../frontend`. A green publish is not recorded here until a later run shows it |
| Trivy | Local image scan clean for HIGH/CRITICAL. The CI scan job on `d5f4f6c` succeeded |
| Terraform/AWS | HCL validates. Apply and destroy not done |
| Kubernetes/Helm | Chart renders and kubeconform is clean. Not installed on a cluster |
| Prometheus/Grafana | Local scrape and dashboard provisioning worked. In-cluster install not done |
| Docs/presentation | Written, including 8 slides. Video not recorded |

## Blockers

- No AWS credentials, so plan/apply/destroy and a real EKS install cannot be finished here
- The first Actions publish was denied by GHCR (`write_package`). The workflow change after that run is the fix; a green package push is not recorded here until a later run shows it
- No Argo CD control plane
- Presentation video cannot honestly include those live systems until you run them

## Manual steps left

1. Create a GitHub repository secret only if you later add a deploy job. The current publish job uses `GITHUB_TOKEN`. Make the GHCR packages public or create an image pull secret.
2. Copy `.env.example` to `.env` and set a real `POSTGRES_PASSWORD` before Compose.
3. Configure AWS credentials. Copy `terraform/terraform.tfvars.example` to `terraform.tfvars`. Run `terraform plan`. Apply only if you accept the cost. Run `terraform destroy` the same day.
4. `aws eks update-kubeconfig --region ap-south-1 --name taskboard-eks`
5. Create Secret `taskboard-db` in namespace `taskboard`. Install the Helm release with your GHCR names and the commit SHA.
6. Install an ingress controller, Metrics Server, and kube-prometheus-stack if you want Ingress, HPA, and the ServiceMonitor.
7. Replace `repoURL` in `gitops/argocd/application.yaml` and apply it only after Argo CD is installed.
8. Record the demo video from `demo/DEMO_SCRIPT.md` and commit the file under `demo/`.

## Commands to run next

```bash
cp .env.example .env
docker compose up --build
cd backend && pytest -q
cd terraform && terraform init && terraform plan
helm template taskboard ./helm/taskboard -n taskboard
```

After AWS credentials exist:

```bash
cd terraform
terraform apply -var-file=terraform.tfvars
aws eks update-kubeconfig --region ap-south-1 --name taskboard-eks
```

## Cost and destroy

EKS standard support is billed at $0.10 per hour for the control plane. Version 1.35 is in standard support through 27 March 2027, so the extended-support surcharge does not apply to that version on 16 October 2026. A NAT gateway adds an hourly charge and a data-processing charge. Two `t3.medium` nodes add compute and disk. Confirm current prices in the AWS calculator before apply.

```bash
helm uninstall taskboard -n taskboard
kubectl delete namespace taskboard
kubectl delete namespace taskboard-troubleshoot
cd terraform && terraform destroy -var-file=terraform.tfvars
```

## Recommended commits

These were the intended local sequence if the push section below does not already list the SHAs:

1. API, Alembic, and tests
2. React UI
3. Dockerfiles and Compose
4. GitHub Actions
5. Terraform
6. Helm, Argo CD, monitoring, troubleshooting
7. Docs, slides, and this status file

## Push

Pushed branch `main` to `https://github.com/ramneek3/taskboard.git` only. `origin` was not changed and was not pushed to.

The first attempt failed because the GitHub token lacked the `workflow` scope. After that scope was granted, `main` was created on the remote at `f0909c5`. This status correction is a later commit on the same branch.

Local commits, oldest first:

| SHA | Subject |
| --- | --- |
| `c1ff1a5` | Initialize project |
| `56e7ce2` | Add the TaskBoard API, Alembic migration, and tests |
| `45d99b5` | Add the React task board |
| `81922ca` | Containerize TaskBoard with Compose |
| `df5b3c1` | Add the GitHub Actions test, scan, and publish pipeline |
| `89c6168` | Add the Terraform VPC and EKS configuration |
| `2eced98` | Add the Helm release, Argo CD app, and monitoring assets |
| `be26596` | Document the architecture, operations, and presentation |

`f0909c5` recorded the earlier failed attempt and is the first commit that reached GitHub. This file's push section was corrected after that push succeeded.
