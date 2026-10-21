#!/usr/bin/env bash
# Shared setup for the numbered AWS scripts. Each script logs to logs/<name>.log
# so the run can be reviewed afterwards. Secrets are never written to the logs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

export AWS_REGION="${AWS_REGION:-ap-south-1}"
export AWS_DEFAULT_REGION="$AWS_REGION"
export CLUSTER_NAME="${CLUSTER_NAME:-taskboard-eks}"
export APP_NS="taskboard"

for b in /opt/homebrew/bin "$HOME/.homebrew/bin" /usr/local/bin; do
  [ -d "$b" ] && PATH="$b:$PATH"
done
export PATH

mkdir -p logs
LOG="logs/$(basename "$0" .sh).log"
exec > >(tee -a "$LOG") 2>&1
echo
echo "=== $(basename "$0") started $(date '+%Y-%m-%d %H:%M:%S %Z') ==="

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
need() { command -v "$1" >/dev/null || { echo "Missing $1. Run scripts/aws/00-install-tools.sh first."; exit 1; }; }
done_msg() { printf '\n\033[1;32m=== %s finished OK. Tell Claude: "%s done" ===\033[0m\n' "$(basename "$0")" "$(basename "$0" .sh)"; }
trap 'rc=$?; [ $rc -ne 0 ] && printf "\n\033[1;31m=== %s FAILED (exit %s). Tell Claude: \"%s failed\" ===\033[0m\n" "$(basename "$0")" "$rc" "$(basename "$0" .sh)"' EXIT
