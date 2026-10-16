# Kubernetes bootstrap

`namespace.yaml` creates the `taskboard` namespace. The running application is the Helm release in `helm/taskboard`, not a hand-written Deployment.

The database password is created out of band:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl -n taskboard create secret generic taskboard-db \
  --from-literal=username=taskboard \
  --from-literal=password='REPLACE_WITH_A_LONG_RANDOM_PASSWORD' \
  --from-literal=database=taskboard
```

Then install the chart. See `docs/DEPLOYMENT.md`.

Broken manifests for the classroom exercise live in `troubleshooting/` and use the namespace `taskboard-troubleshoot`. They are not part of this release.
