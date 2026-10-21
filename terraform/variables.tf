variable "aws_region" {
  description = "AWS region for the VPC and EKS cluster. The AWS Organization SCP on this account only allows ap-southeast-2 (Sydney)."
  type        = string
  default     = "ap-southeast-2"
}

variable "environment" {
  description = "Name prefix used in tags."
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
  default     = "taskboard-eks"
}

variable "cluster_version" {
  description = "EKS Kubernetes version. 1.35 is in Amazon EKS standard support through 2027-03-27. 1.34, 1.36, and 1.37 are the other standard-support versions as of 2026-10-16."
  type        = string
  default     = "1.35"
}

variable "cluster_enabled_log_types" {
  description = "EKS control plane log types sent to CloudWatch. Empty avoids log storage charges."
  type        = list(string)
  default     = []
}

variable "node_instance_types" {
  description = "Instance types for the managed node group. m7i-flex.large is free-tier eligible, so it also works on AWS Free plan accounts."
  type        = list(string)
  default     = ["m7i-flex.large"]
}

variable "node_min_size" {
  description = "Minimum node count."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum node count."
  type        = number
  default     = 3
}

variable "node_desired_size" {
  description = "Desired node count. 2 x m7i-flex.large (29 pods each) fits the app, Argo CD, and kube-prometheus-stack."
  type        = number
  default     = 2
}

variable "vpc_cidr" {
  description = "CIDR for the TaskBoard VPC."
  type        = string
  default     = "10.20.0.0/16"
}
