#!/usr/bin/env bash
# Port-forwards Argo CD, Prometheus, and Grafana to localhost and prints the
# admin passwords to this terminal only (they are not written to the log).
source "$(dirname "$0")/lib.sh"
need kubectl

pkill -f "kubectl.*port-forward" 2>/dev/null || true
kubectl -n argocd port-forward svc/argocd-server 8080:80 >/dev/null 2>&1 &
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090 >/dev/null 2>&1 &
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3001:80 >/dev/null 2>&1 &
sleep 4

LB=$(kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
cat <<MSG
TaskBoard (Ingress) : http://$LB
Argo CD             : http://localhost:8080   user: admin
Prometheus targets  : http://localhost:9090/targets
Grafana             : http://localhost:3001   user: admin
MSG
# Shown on screen only; stripped from the log by printing straight to the tty.
{
  echo "Argo CD password : $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"
  echo "Grafana password : $(kubectl -n monitoring get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 -d)"
} > /dev/tty
echo "Port-forwards run in the background. Keep this Terminal window open."
done_msg
wait
