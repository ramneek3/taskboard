output "aws_region" {
  description = "Region the stack targets."
  value       = var.aws_region
}

output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API endpoint."
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "Kubernetes version requested for the cluster."
  value       = var.cluster_version
}

output "vpc_id" {
  description = "VPC id."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet ids."
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "Private subnet ids."
  value       = module.vpc.private_subnets
}

output "configure_kubectl" {
  description = "Command that writes a kubeconfig for this cluster after apply."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
