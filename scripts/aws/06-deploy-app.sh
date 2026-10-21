#!/usr/bin/env bash
# Database secret + `helm upgrade --install` of the TaskBoard chart.
source "$(dirname "$0")/lib.sh"
need kubectl; need helm; need curl

TAG=$(awk '/^backend:/{f=1} f && /tag:/{print $2; exit}' helm/taskboard/values-eks.yaml)
step "Image tag from values-eks.yaml: $TAG"
for img in backend frontend; do
  tok=$(curl -fsS "https://ghcr.io/token?scope=repository:ramneek3/taskboard/$img:pull" | sed -E 's/.*"token":"([^"]+)".*/\1/')
  code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $tok" \
    -H 'Accept: application/vnd.oci.image.index.v1+json,application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json' \
    "https://ghcr.io/v2/ramneek3/taskboard/$img/manifests/$TAG")
  echo "ghcr.io/ramneek3/taskboard/$img:$TAG anonymous pull -> HTTP $code"
  if [ "$code" != "200" ]; then
    echo "The $img package is not public. GitHub > your profile > Packages > taskboard/$img > Package settings > Change visibility > Public. Then re-run."
    exit 1
  fi
done

step "Database secret"
if ! kubectl -n "$APP_NS" get secret taskboard-db >/dev/null 2>&1; then
  kubectl -n "$APP_NS" create secret generic taskboard-db \
    --from-literal=username=taskboard \
    --from-literal=password="$(openssl rand -base64 18 | tr -d '/+=')" \
    --from-literal=database=taskboard >/dev/null
  echo "Created secret $APP_NS/taskboard-db (password not logged)."
fi

step "helm upgrade --install taskboard"
helm upgrade --install taskboard ./helm/taskboard -n "$APP_NS" \
  -f helm/taskboard/values-eks.yaml --wait --timeout 10m

step "Release status"
helm list -n "$APP_NS"
kubectl -n "$APP_NS" get pods -o wide
kubectl -n "$APP_NS" get svc
kubectl -n "$APP_NS" get ingress
kubectl -n "$APP_NS" get hpa
kubectl -n "$APP_NS" get pvc

LB=$(kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
step "Smoke test through the Ingress: http://$LB"
for i in $(seq 1 30); do curl -fsS -m 10 "http://$LB/api/stats" && break; echo "waiting for NLB DNS..."; sleep 10; done || true
echo
curl -s -o /dev/null -w "frontend / -> HTTP %{http_code}\n" "http://$LB/"
echo "Open in your browser: http://$LB"
done_msg
