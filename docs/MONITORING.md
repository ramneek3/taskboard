# Monitoring

## Metrics the API actually emits

`GET /metrics` includes:

| Name | Type | Meaning |
| --- | --- | --- |
| `http_requests_total` | counter | Requests labeled by method, handler, and status |
| `http_request_duration_seconds` | histogram | Latency. Quantiles use the `_bucket` series |
| `http_request_duration_highr_seconds` | histogram | Higher-resolution latency histogram from the instrumentator |
| `http_request_size_bytes` | summary | Request size |
| `http_response_size_bytes` | summary | Response size |
| `taskboard_tasks_created_total` | counter | Creates, labeled by `priority` |
| `taskboard_tasks_updated_total` | counter | Updates |
| `taskboard_tasks_deleted_total` | counter | Deletes |
| `taskboard_tasks_by_status` | gauge | Current rows, labeled by `status` |

The gauge is collected when Prometheus scrapes `/metrics`, so it matches the database at scrape time. Counters move when the API handles a create, update, or delete.

## Local Prometheus

`monitoring/prometheus.yml` scrapes `backend:8000` at `/metrics` with job name `taskboard-backend`.

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml --profile observability up --build
```

Grafana is provisioned with datasource uid `prometheus` and the dashboard file `monitoring/grafana/dashboards/taskboard.json`. Queries in that file use the metric names above, including:

- `sum(rate(http_requests_total[5m]))`
- `sum(rate(http_requests_total{status=~"5.."}[5m]))`
- `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`
- `sum by (status) (taskboard_tasks_by_status)`
- `sum(rate(taskboard_tasks_created_total[5m]))`

## Cluster

`monitoring/prometheus-values.yaml` is a values file for kube-prometheus-stack. It selects ServiceMonitors in all namespaces and tells the Grafana sidecar to load ConfigMaps labeled `grafana_dashboard=1`. Create the Grafana admin secret before install. Do not put that password in git.

The Helm chart renders a ServiceMonitor that selects the backend Service and scrapes port `http` at path `/metrics`. It also renders the same dashboard JSON as a ConfigMap.

On EKS, kube-prometheus-stack scraped both backend pods through the ServiceMonitor (targets `UP`) and Grafana loaded the `TaskBoard API` dashboard from the chart. A local Compose observability stack is also available for development.
