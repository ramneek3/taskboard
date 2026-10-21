#!/usr/bin/env bash
# Installs the CLIs used by the other scripts with Homebrew.
source "$(dirname "$0")/lib.sh"

step "Homebrew"
if ! command -v brew >/dev/null; then
  echo "Homebrew not found. Install it from https://brew.sh then re-run this script."
  exit 1
fi
brew --version | head -1

step "Installing awscli, terraform, kubectl, helm"
brew install awscli kubectl helm
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

step "Versions"
aws --version
terraform version | head -1
kubectl version --client
helm version --short
done_msg
