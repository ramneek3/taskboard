# TaskBoard

A task board with a React UI, a FastAPI API, and PostgreSQL, packaged the way a small production service is packaged.

## What it demonstrates

- The application works before any cluster exists.
- Tests gate the image build.
- Images are scanned, then published by git SHA.
- Terraform describes the AWS network and EKS cluster.
- Helm and Argo CD describe the running release.
- Prometheus scrapes `/metrics` and Grafana charts those series.

## What this deck does not claim

Slides describe the repository. A green GitHub Actions run, an applied EKS cluster, and an Argo CD sync are live steps you perform and show. They are not assumed to have happened because the files exist.
