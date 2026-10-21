#!/usr/bin/env bash
# Source this in Terminal before recording:   source ~/Desktop/taskboard/scripts/aws/demo-env.sh
# It puts the macOS kubectl, helm, and terraform from .demo/bin on PATH and points
# them at the EKS cluster. .demo/ is gitignored; delete it after terraform destroy.
DEMO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"
export PATH="$DEMO_ROOT/.demo/bin:$PATH"
export KUBECONFIG="$DEMO_ROOT/.demo/kubeconfig"
export AWS_SHARED_CREDENTIALS_FILE="$DEMO_ROOT/.demo/aws-credentials"
export AWS_REGION=ap-southeast-2 AWS_DEFAULT_REGION=ap-southeast-2
export TF_DATA_DIR="$DEMO_ROOT/.demo/tfdata"
cd "$DEMO_ROOT"
echo "TaskBoard demo shell ready in $DEMO_ROOT"
kubectl config current-context
