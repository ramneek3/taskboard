# Security

## Secrets

Committed config uses placeholders such as `replace-with-a-long-random-password`. Compose requires `POSTGRES_PASSWORD` from the environment. The Helm chart reads the database password from Secret `taskboard-db` and does not render the password into values. `.gitignore` excludes `.env`, virtualenvs, Terraform state, kubeconfigs, and private keys.

The database role name `taskboard` is an identifier. It is not the password.

## Runtime

| Process | User |
| --- | --- |
| API container | uid 10001 |
| Nginx container | uid 101 |
| Postgres server | uid 70 |

The API container sets a read-only root filesystem in the Helm chart and writes only to an emptyDir on `/tmp`. Nginx stays writable at startup so the image entrypoint can render `BACKEND_UPSTREAM` into the config. Both containers drop all capabilities and set `allowPrivilegeEscalation: false` in the chart.

## Trivy

The workflow scans both images with `aquasecurity/trivy-action` and `exit-code: 1` for severity `HIGH,CRITICAL`. Unfixed findings are not ignored. There is no `.trivyignore` file.

A local scan of the images built in this workspace is recorded in `IMPLEMENTATION_STATUS.md`. That scan is not a GitHub Actions run.

## Pipeline permissions

Pull request jobs set `contents: read` only. `packages: write` and the GHCR login exist only on the publish job, and that job runs only for a push to `main`.

## Application

- Task titles are stripped and rejected when blank.
- Status and priority are enums.
- `/ready` returns 503 when the database check fails.
- CORS is open (`*`) so the classroom UI can call the API. Restrict `allow_origins` before a public deployment.

## Base image findings with no Debian fix

The API image is `python:3.12-alpine` with `apk upgrade`, not Debian. That choice avoids shipping Debian packages whose HIGH findings had no fixed version at scan time. If a later scan reports a HIGH or CRITICAL CVE with a fixed package version, upgrade the base image or the pinned dependency. Add a `.trivyignore` entry only for a single CVE you have reviewed, with the reason in this file.
