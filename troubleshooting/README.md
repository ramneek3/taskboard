# Disposable troubleshooting exercise

These manifests are not part of the Helm release. Apply them only in `taskboard-troubleshoot`, then delete that namespace.

```bash
kubectl apply -f troubleshooting/namespace.yaml
kubectl apply -f troubleshooting/broken-image.yaml
kubectl apply -f troubleshooting/broken-service.yaml
kubectl delete namespace taskboard-troubleshoot
```

Symptom, commands, cause, and fix are in `docs/TROUBLESHOOTING.md`.
