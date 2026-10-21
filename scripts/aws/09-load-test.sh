#!/usr/bin/env bash
# Sends traffic through the Ingress so Grafana panels and the HPA have data.
source "$(dirname "$0")/lib.sh"
need kubectl
LB=$(kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
COUNT="${COUNT:-2000}"
step "Sending $COUNT requests (8 in parallel) to http://$LB/api/tasks"
seq 1 "$COUNT" | xargs -P 8 -I{} curl -s -o /dev/null "http://$LB/api/tasks"
kubectl -n "$APP_NS" get hpa
kubectl -n "$APP_NS" top pods || true
done_msg
