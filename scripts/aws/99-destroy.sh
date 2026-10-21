#!/usr/bin/env bash
# Deletes everything that costs money. Load balancers and EBS volumes created by
# Kubernetes are removed first, otherwise terraform destroy cannot delete the VPC.
source "$(dirname "$0")/lib.sh"
need terraform; need kubectl; need helm; need aws

if kubectl get nodes >/dev/null 2>&1; then
  step "Removing Kubernetes-created AWS resources"
  kubectl -n argocd delete application taskboard --wait=false 2>/dev/null || true
  helm uninstall taskboard -n "$APP_NS" 2>/dev/null || true
  kubectl -n "$APP_NS" delete pvc --all --wait=true 2>/dev/null || true
  helm uninstall ingress-nginx -n ingress-nginx 2>/dev/null || true
  helm uninstall kube-prometheus-stack -n monitoring 2>/dev/null || true
  helm uninstall argocd -n argocd 2>/dev/null || true
  echo "Waiting 90s for the load balancer and volumes to be deleted..."
  sleep 90
fi

step "terraform destroy"
cd terraform
terraform destroy -input=false -auto-approve -var-file=terraform.tfvars

step "Check nothing is left"
aws eks list-clusters --region "$AWS_REGION" --output table
aws elbv2 describe-load-balancers --region "$AWS_REGION" --query 'LoadBalancers[].LoadBalancerName' --output table
aws ec2 describe-volumes --region "$AWS_REGION" --filters Name=status,Values=available --query 'Volumes[].VolumeId' --output table
done_msg
