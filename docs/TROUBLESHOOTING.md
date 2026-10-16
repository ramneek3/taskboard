# Troubleshooting

## API pod not Ready

Symptom: the backend Pod stays `Running` but not `Ready`, or Compose reports the backend unhealthy.

Commands:

```bash
kubectl logs deploy/taskboard-backend -n taskboard
kubectl describe pod -n taskboard -l app.kubernetes.io/component=backend
curl -sS http://127.0.0.1:8000/ready
```

Cause: `/ready` runs `SELECT 1`. Alembic or Postgres is still starting, or Secret `taskboard-db` is missing.

Fix: confirm the Secret exists and the Postgres Pod is Ready. The startup probe allows time for `alembic upgrade head`. Readiness stays failed until the database accepts connections.

## Empty task list and HTTP 500

Symptom: `/api/tasks` returns 500 and the error mentions a missing `tasks` relation.

Cause: the process was started without Alembic. The application does not create tables on startup.

Fix:

```bash
alembic upgrade head
```

The container entrypoint already runs that command.

## ImagePullBackOff exercise

Symptom: a Pod in `taskboard-troubleshoot` shows `ImagePullBackOff` or `ErrImagePull`.

Commands:

```bash
kubectl apply -f troubleshooting/namespace.yaml
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n taskboard-troubleshoot
kubectl describe pod -n taskboard-troubleshoot -l app=broken-image
```

Cause: the manifest references `ghcr.io/example/taskboard-backend:does-not-exist`.

Fix: delete the namespace when you are done. Do not change the Helm release to point at that tag.

```bash
kubectl delete namespace taskboard-troubleshoot
```

## Service has no endpoints

Symptom: a Service exists and requests to it time out. `kubectl get endpoints` shows no addresses.

Commands:

```bash
kubectl apply -f troubleshooting/namespace.yaml
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get svc,endpoints -n taskboard-troubleshoot
kubectl get pods -n taskboard-troubleshoot --show-labels
```

Cause: `broken-service` selects `app=label-that-does-not-exist`. No Pod has that label, so the Service has no endpoints.

Fix: delete the namespace. The Helm Services select `app.kubernetes.io/instance` plus `app.kubernetes.io/component`, and the Pods use the same labels.

## Ingress returns the UI for `/api`

Symptom: `http://taskboard.local/api/tasks` returns HTML.

Cause: the Ingress path `/` was matched first, or no ingress controller is running. An Ingress object does nothing by itself.

Fix: install a controller whose class is `nginx` (or set `ingress.className`). Keep path `/api` as `Prefix` ahead of `/` in the manifest. The chart already orders `/api` before `/`.

## HPA stays at the minimum

Symptom: `kubectl get hpa` shows the backend at `minReplicas` during a small curl loop.

Cause: HPA needs Metrics Server and CPU above the target. `scripts/load-test.sh` sends a short burst of GETs. That often does not move CPU.

Fix: confirm `kubectl top pods` works, then generate real CPU load. The chart sets CPU requests so utilization can be calculated.

## Trivy fails the pipeline

Symptom: the image scan job exits 1.

Cause: a HIGH or CRITICAL finding has a fix, or an unfixed finding is also in scope. The workflow does not set `ignore-unfixed`.

Fix: upgrade the base image (`apk upgrade` is already in both Dockerfiles) or the pinned Python package. If Debian or Alpine has no fixed version, record that single CVE in `docs/SECURITY.md` before considering an ignore entry.

## Terraform plan asks for credentials

Symptom: `terraform plan` errors with `No valid credential sources found`.

Cause: the AWS provider has no credentials. `terraform validate` does not need them. `terraform apply` was not run.

Fix: configure an AWS profile or environment credentials, then run `terraform plan` yourself. Destroy the stack the same day.
