# Monitoring and lessons

## Panels use real series

- `http_requests_total` for rate and 5xx rate
- `http_request_duration_seconds_bucket` for p50 and p95
- `taskboard_tasks_by_status` for the board
- `taskboard_tasks_created_total`, `taskboard_tasks_updated_total`, `taskboard_tasks_deleted_total` for mutations

If a panel is empty, the scrape has not happened yet or the metric name does not match `/metrics`. Check the target before changing the query.

## Lessons

- Liveness and readiness answer different questions. `/health` is cheap. `/ready` checks the database.
- SHA tags connect a running image to a commit. `latest` does not.
- A Helm render and a Terraform validate are real checks, and they are not a running cluster or an AWS bill.
- Unfixed base-image CVEs and fixable library CVEs are different. Upgrade what has a fix.
- Delete the EKS cluster and the NAT gateway when the demo ends.

## Still yours to record

The presentation video has to show the live pipeline, plan or apply, Argo CD, pods, Prometheus, and Grafana. Record that after those systems are actually up.
