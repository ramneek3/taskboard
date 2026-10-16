# Terraform, Kubernetes, Helm, Argo CD

## Terraform

Region `ap-south-1`. One VPC, two public subnets, two private subnets, one NAT gateway, one EKS managed node group. Default Kubernetes version `1.35` (EKS standard support through 27 March 2027).

`terraform validate` checks the configuration. `terraform apply` creates billable resources. Destroy them the same day.

## Helm

The chart renders two replicas of the UI and the API, ClusterIP Services, Postgres with a PVC, probes, requests and limits, an Ingress, a backend HPA, a ServiceMonitor, and a Grafana dashboard ConfigMap. The database password comes from a Secret you create. It is not in `values.yaml`.

`helm template` is a render. Pods are `Running` only after an install against a cluster.

## Argo CD

`gitops/argocd/application.yaml` points at `helm/taskboard` on `main`. Replace the repo URL. The file does not prove the app is synced.

## Exercise

ImagePullBackOff and the selector mismatch live in namespace `taskboard-troubleshoot`. They are not in the chart.
