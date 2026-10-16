# Demo script

Use this order in the presentation. The shot list and the recording checklist are in [demo/DEMO_SCRIPT.md](../demo/DEMO_SCRIPT.md).

1. Open the slides in `docs/presentation/` and state what TaskBoard is: a task API and UI with the path from a laptop to a monitored cluster.
2. Show the React UI on http://localhost:3000. Create a task, advance its status, and delete it.
3. Show http://localhost:8000/docs and `GET /health`, `GET /ready`, and `GET /metrics`.
4. Show `alembic_version` and `tasks` in Postgres.
5. Show `pytest -q` and the workflow file. Say clearly whether a GitHub Actions run has actually gone green. Do not claim a run you have not opened.
6. Show the two Dockerfiles and `docker compose ps`.
7. Show a Trivy invocation and the result you actually have.
8. Show `terraform validate` output and the VPC/EKS files. If you have not applied, say the cluster does not exist yet.
9. Render the chart with `helm template` and explain that render is not a running cluster.
10. If Argo CD is installed, show the Application. If it is not, show the manifest and say it has not synced.
11. If Prometheus is scraping, show the target. If Grafana has data, show the TaskBoard dashboard. Name the metrics on the panels.
12. Apply the troubleshooting manifests in `taskboard-troubleshoot`, show ImagePullBackOff or empty endpoints, then delete that namespace.

A video was not recorded in the workspace that produced this repository. Record it yourself after the live AWS, Actions, and cluster steps exist. Do not upload a video that pretends those systems ran.
