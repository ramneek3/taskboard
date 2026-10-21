#!/usr/bin/env bash
# Applies the saved plan (VPC + EKS, ~15-20 minutes) and points kubectl at the cluster.
# Billing starts here. Run 99-destroy.sh when you are finished.
source "$(dirname "$0")/lib.sh"
need terraform; need aws; need kubectl

cd terraform
[ -f tfplan ] || { echo "No tfplan. Run 02-terraform-plan.sh first."; exit 1; }

step "terraform apply (this takes 15-20 minutes)"
terraform apply -input=false tfplan
terraform output

step "kubeconfig"
aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"
kubectl get nodes -o wide
done_msg
