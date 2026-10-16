# Terraform

This directory describes an AWS VPC and an EKS cluster in `ap-south-1`. It is not applied from this workspace.

## Layout

- `versions.tf` — Terraform `>= 1.7` and the AWS provider
- `variables.tf` — region, cluster name, Kubernetes version, node size
- `main.tf` — VPC module and EKS module
- `outputs.tf` — cluster endpoint, subnet ids, kubeconfig command
- `terraform.tfvars.example` — copy to `terraform.tfvars` (gitignored)

The default Kubernetes version is **1.35**. As of 16 October 2026, Amazon EKS standard support covers 1.34, 1.35, 1.36, and 1.37. Version 1.35 stays in standard support through 27 March 2027. Override `cluster_version` in tfvars if you want 1.37.

## Commands

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
aws eks update-kubeconfig --region ap-south-1 --name taskboard-eks
```

`terraform plan` and `terraform apply` need AWS credentials. Do not commit those credentials or any `*.tfstate` file.

## Destroy

```bash
cd terraform
terraform destroy -var-file=terraform.tfvars
```

Destroy the cluster when the demo is over. See `docs/DEPLOYMENT.md` for the cost notes.
