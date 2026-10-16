# Deployment

## Local

```bash
cp .env.example .env
# Replace the password placeholders.
docker compose up --build
```

Compose starts Postgres, waits until `pg_isready` succeeds, then starts the API. The API entrypoint runs `alembic upgrade head` and then Uvicorn on `0.0.0.0:8000`. Nginx listens on 8080 inside the container and is published on host port 3000.

## Images

GitHub Actions publishes, only from a push to `main`:

```text
ghcr.io/<owner>/<repo>/backend:<40-character-sha>
ghcr.io/<owner>/<repo>/frontend:<40-character-sha>
```

Make the packages public, or create an image pull secret named in `imagePullSecrets`, before the cluster can pull them.

## Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl -n taskboard create secret generic taskboard-db \
  --from-literal=username=taskboard \
  --from-literal=password='REPLACE_WITH_A_LONG_RANDOM_PASSWORD' \
  --from-literal=database=taskboard

helm upgrade --install taskboard ./helm/taskboard \
  -n taskboard \
  --set backend.image=ghcr.io/OWNER/REPO/backend \
  --set frontend.image=ghcr.io/OWNER/REPO/frontend \
  --set backend.tag=GIT_SHA \
  --set frontend.tag=GIT_SHA
```

`helm template` renders manifests. It does not contact a cluster. A real install also needs:

- a StorageClass that can bind the Postgres PVC
- an Ingress controller whose class matches `ingress.className` (default `nginx`)
- Metrics Server if you want the HPA to scale
- the Prometheus Operator if you want the ServiceMonitor to be scraped

Replace `repoURL` in `gitops/argocd/application.yaml`, then:

```bash
kubectl apply -f gitops/argocd/application.yaml
```

This repository does not record an Argo CD sync result. Apply the Application yourself and read `argocd app get taskboard`.

## Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
aws eks update-kubeconfig --region ap-south-1 --name taskboard-eks
```

The default cluster version is 1.35. Amazon EKS standard support on 16 October 2026 includes 1.34, 1.35, 1.36, and 1.37. Version 1.35 remains in standard support through 27 March 2027. Extended-support versions cost more. Do not commit `terraform.tfvars` or `*.tfstate`.

`terraform validate` was run here. `terraform plan` stopped because this environment has no AWS credentials. Nothing was applied.

## Cost

These are public list-price shapes, not a quote. Check the AWS pricing calculator before you apply.

- EKS control plane in standard support: $0.10 per hour. Extended support is higher. Version 1.35 is still in standard support on the date above.
- One NAT gateway: hourly charge plus a per-GB data processing charge. The config uses a single NAT to keep the classroom bill smaller than one NAT per AZ.
- Two `t3.medium` nodes in `ap-south-1`, plus their EBS volumes. Set `node_desired_size` and `node_min_size` to 1 in your private tfvars for a short demo.
- Control plane logs are off by default so CloudWatch log storage is not turned on accidentally.
- A load balancer created by an ingress controller is extra and is not destroyed by `terraform destroy` if it was created by Kubernetes.

Leaving the cluster up overnight is a real charge. Destroy it the same day you apply it.

## Destroy

```bash
helm uninstall taskboard -n taskboard
kubectl delete namespace taskboard
kubectl delete namespace taskboard-troubleshoot
cd terraform
terraform destroy -var-file=terraform.tfvars
```

Confirm in the AWS console that the EKS cluster, node group, NAT gateway, and load balancers are gone.
