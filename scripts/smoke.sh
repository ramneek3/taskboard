#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://127.0.0.1:8000}"

curl -fsS "$BASE/health"
echo
curl -fsS "$BASE/ready"
echo
curl -fsS -H 'content-type: application/json' \
  -d '{"title":"Smoke task","priority":"HIGH","assignee":"Alex"}' \
  "$BASE/api/tasks"
echo
curl -fsS "$BASE/api/tasks"
echo
curl -fsS "$BASE/api/stats"
echo
curl -fsS "$BASE/metrics" | awk '/^# TYPE (http_requests_total|http_request_duration_seconds|taskboard_tasks_created_total|taskboard_tasks_by_status) /{print}'
