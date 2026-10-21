# Rubric mapping

Scores below describe what is in the repository and what was executed in the workspace. They are not a grade.

| Module | Points | In the repo | Verified here | Still manual |
| --- | --- | --- | --- | --- |
| M1 Application | 10 | React UI, FastAPI CRUD, Postgres, Alembic | Compose stack served the UI and CRUD. Pytest and a host SQLite smoke test passed. | Browser screenshot for the grader |
| M2 Tests | 10 | 13 backend tests, `pytest.ini`, frontend `node --test` | `pytest` and `npm test` passed | Paste the terminal output into the submission if a screenshot is required |
| M3 Git and GitHub | 5 | `.gitignore`, this repository | Pushed to `ramneek3/taskboard` on GitHub | Public repo URL and a history screenshot |
| M4 Docker | 10 | Multi-stage frontend, non-root images, Compose healthchecks | Images built. Compose reached healthy. CRUD through Nginx worked. | — |
| M5 CI/CD | 15 | Workflow builds, tests, scans, and pushes SHA tags to GHCR only on `main` | `actionlint` passed. No Actions run was executed. | A green run URL and the GHCR package page |
| M6 Trivy | 5 | Scan step fails on HIGH and CRITICAL for both images | CI Trivy runs report 0 HIGH/CRITICAL on both images | Explain that result in the video |
| M7 Terraform | 15 | VPC, two public subnets, private subnets, NAT, EKS, tfvars example | `fmt`, `init`, `validate` passed. `plan` blocked on missing AWS credentials. Apply was not run. | `plan` with credentials, console screenshots, `destroy` |
| M8 Kubernetes and Helm | 15 | Namespace, chart, probes, PVC, Services, Ingress, HPA, 2 replicas | `helm lint`, `helm template`, kubeconform. No cluster. | `helm upgrade`, `kubectl get pods` |
| M9 Prometheus and Grafana | 10 | `/metrics`, ServiceMonitor, dashboard JSON, Compose profile | `/metrics` names match the dashboard. Cluster install was not run. | Prometheus targets and a live Grafana panel |
| M10 Docs and presentation | 5 | README, docs, 8 slides, demo script | Written. No presentation video. | Record and upload the video |

The healthy Helm release does not include the broken image or the broken Service. Those files are an exercise under `troubleshooting/`.
