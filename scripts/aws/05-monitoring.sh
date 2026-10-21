#!/usr/bin/env bash
# kube-prometheus-stack (Prometheus Operator + Grafana). Must run before the app,
# because the app chart contains a ServiceMonitor, which needs the Operator's CRDs.
source "$(dirname "$0")/lib.sh"
need kubectl; need helm

step "Grafana admin secret"
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
if ! kubectl -n monitoring get secret grafana-admin >/dev/null 2>&1; then
  kubectl -n monitoring create secret generic grafana-admin \
    --from-literal=admin-user=admin \
    --from-literal=admin-password="$(openssl rand -base64 18 | tr -d '/+=')" >/dev/null
  echo "Created secret monitoring/grafana-admin (password not logged)."
fi

step "kube-prometheus-stack"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update
helm repo update prometheus-community
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring -f monitoring/prometheus-values.yaml --wait --timeout 15m

kubectl -n monitoring get pods
done_msg
