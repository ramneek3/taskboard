#!/usr/bin/env bash
# Installs Argo CD and hands the taskboard release over to it (GitOps).
source "$(dirname "$0")/lib.sh"
need kubectl; need helm

step "Argo CD"
helm repo add argo https://argoproj.github.io/argo-helm --force-update
helm repo update argo
helm upgrade --install argocd argo/argo-cd -n argocd --create-namespace \
  --set-string configs.params."server\.insecure"=true \
  --set dex.enabled=false --set notifications.enabled=false \
  --wait --timeout 10m

step "Application taskboard"
kubectl apply -f gitops/argocd/application.yaml
for i in $(seq 1 30); do
  s=$(kubectl -n argocd get application taskboard -o jsonpath='{.status.sync.status}/{.status.health.status}' 2>/dev/null || true)
  echo "sync/health: $s"
  [ "$s" = "Synced/Healthy" ] && break; sleep 10
done
kubectl -n argocd get applications
done_msg
