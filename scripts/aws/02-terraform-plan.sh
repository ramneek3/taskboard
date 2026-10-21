#!/usr/bin/env bash
# terraform init + plan. Writes terraform/tfplan and logs/terraform-plan.txt.
source "$(dirname "$0")/lib.sh"
need terraform; need aws

cd terraform
[ -f terraform.tfvars ] || { cp terraform.tfvars.example terraform.tfvars; echo "Created terraform/terraform.tfvars from the example."; }

step "terraform init"
terraform init -input=false

step "terraform validate"
terraform validate

step "terraform plan"
terraform plan -input=false -var-file=terraform.tfvars -out=tfplan | tee ../logs/terraform-plan.txt
done_msg
