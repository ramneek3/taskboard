#!/usr/bin/env bash
# gp3 StorageClass, ingress-nginx (AWS NLB), and Metrics Server for the HPA.
source "$(dirname "$0")/lib.sh"
need kubectl; need helm

step "Namespace and gp3 StorageClass"
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/storageclass-gp3.yaml
if kubectl get storageclass gp2 >/dev/null 2>&1; then
  kubectl annotate storageclass gp2 storageclass.kubernetes.io/is-default-class=false --overwrite
fi
kubectl get storageclass

step "Helm repos"
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx --force-update
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/ --force-update
helm repo update

step "ingress-nginx controller (creates an AWS Network Load Balancer)"
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  -n ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set-string controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"=nlb \
  --wait --timeout 10m

step "Metrics Server"
helm upgrade --install metrics-server metrics-server/metrics-server \
  -n kube-system --wait --timeout 5m

step "Load balancer hostname"
for i in $(seq 1 30); do
  LB=$(kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)
  [ -n "$LB" ] && break; sleep 10
done
echo "Ingress load balancer: ${LB:-<pending>}"
kubectl get pods -A
done_msg
