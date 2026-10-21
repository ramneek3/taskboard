#!/usr/bin/env bash
# Confirms the AWS CLI is signed in. Run `aws configure` yourself first.
source "$(dirname "$0")/lib.sh"
need aws

step "Who am I"
aws sts get-caller-identity --output table

step "EKS versions available in $AWS_REGION"
aws eks describe-cluster-versions --region "$AWS_REGION" \
  --query 'clusterVersions[].[clusterVersion,versionStatus]' --output table 2>/dev/null \
  || echo "(describe-cluster-versions not supported by this CLI version; skipping)"

step "Existing EKS clusters in $AWS_REGION"
aws eks list-clusters --region "$AWS_REGION" --output table
done_msg
