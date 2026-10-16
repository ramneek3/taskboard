#!/usr/bin/env bash
set -euo pipefail
URL="${URL:-http://taskboard.local/api/tasks}"
COUNT="${COUNT:-200}"
for _ in $(seq 1 "$COUNT"); do
  curl -sS -o /dev/null "$URL" || true
done
echo "Sent ${COUNT} requests to ${URL}"
