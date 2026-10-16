# Demo shot list

Record only what is on screen. If a system is not deployed, say so and show the file plus the command that is blocked.

## Checklist before you press record

- [ ] `docker compose ps` shows frontend, backend, and postgres healthy, or you are about to start them on camera
- [ ] AWS credentials work if you will run `terraform plan` or `apply`
- [ ] You know the GitHub Actions URL you will open
- [ ] GHCR shows the SHA tags you will point at, or you will show the workflow file and say they are not published yet
- [ ] kubectl context is the cluster you mean
- [ ] Prometheus and Grafana URLs work, or you will not claim they do
- [ ] `taskboard-troubleshoot` does not already contain the broken manifests
- [ ] You will run `terraform destroy` after the recording if you applied

## Shots

1. Slides `docs/presentation/01-overview.md` through `08-monitoring-and-lessons.md`. State the architecture in one minute.
2. Browser at http://localhost:3000. Create a task, change status, delete it. Show the empty state.
3. http://localhost:8000/docs and a curl of `/health`, `/ready`, and `/metrics`.
4. `psql` or `docker compose exec postgres psql` showing `tasks` and `alembic_version`.
5. Terminal: `cd backend && pytest -q`.
6. GitHub Actions run for a real push, from the Actions tab. If you have no run, show `.github/workflows/ci-cd.yml` and say it has not run.
7. `docker compose ps` and both Dockerfiles. Non-root users: uid 10001 and uid 101.
8. Trivy log for both images. Read one line of the result out loud.
9. GHCR packages with the commit SHA. Skip the click-through if the packages are not there.
10. `terraform validate` and, with credentials, `terraform plan`. Console proof only after apply.
11. `helm template` versus `kubectl get pods,svc,ingress,hpa -n taskboard` after a real install.
12. Argo CD application health. If Argo is not installed, show `gitops/argocd/application.yaml` and say there is no sync status.
13. Prometheus target UP for the backend, then the Grafana TaskBoard dashboard with a request-rate or task panel.
14. Apply `troubleshooting/broken-image.yaml` or `broken-service.yaml` in `taskboard-troubleshoot`. Show the symptom and delete the namespace.

## Recording status for the workspace that built this repo

No presentation video was recorded. The environment had no AWS account, no GitHub Actions execution, and no EKS cluster, so a video of those steps would have been fabricated. Local Compose, tests, Trivy, Helm render, and Terraform validate were run. See `IMPLEMENTATION_STATUS.md`.
