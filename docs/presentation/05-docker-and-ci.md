# Docker and CI

## Images

- Backend: `python:3.12-alpine`, `apk upgrade`, uid 10001, entrypoint runs Alembic then Uvicorn.
- Frontend: Node build stage, then `nginxinc/nginx-unprivileged` with `apk upgrade`, uid 101, listen 8080.

Compose healthchecks wait for Postgres, then `/ready`, then the UI.

## Workflow

On pull request and on push to `main`: test, frontend build, Compose config, both image builds, Trivy.

On push to `main` only: log in to GHCR and push

```text
ghcr.io/<owner>/<repo>-backend:<sha>
ghcr.io/<owner>/<repo>-frontend:<sha>
```

Pull request tokens cannot write packages. The tag is the commit SHA, not `latest`.
