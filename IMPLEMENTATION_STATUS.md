# Implementation status

Evidence log for the TaskBoard capstone. Updated 21 October 2026 after the live AWS deployment.

## Rubric

| Module | State | Evidence |
| --- | --- | --- |
| M1 App | Done | FastAPI CRUD + `/health` `/ready` `/metrics`, Alembic `0001_create_tasks`, React UI. Task created through the EKS Ingress and read back from Postgres |
| M2 Tests | Done | 13 pytest (SQLite, `conftest.py`, `pytest.ini`) + 4 frontend tests, all green in CI |
| M3 Git | Done | Public repo `ramneek3/taskboard`, descriptive commits, `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv`, tfstate, tfvars |
| M4 Docker | Done | Multi-stage frontend (Node → nginx-unprivileged), non-root API (uid 10001), Compose runs postgres, backend, frontend |
| M5 CI/CD | Done | `.github/workflows/ci-cd.yml` on push to `main`: pytest, frontend build, both images, GHCR push tagged with the commit SHA, GitOps tag bump |
| M6 Trivy | Done | Trivy gate on both images, `HIGH,CRITICAL`, `exit-code: 1`; scans clean |
| M7 Terraform | Applied | `terraform plan`: 59 to add. Applied in `ap-southeast-2`: VPC `vpc-02372d42e615793b9`, 2 public + 2 private subnets, NAT gateway, EKS `taskboard-eks` 1.35, node group 2 × `m7i-flex.large`. `terraform plan` afterwards: no changes |
| M8 Kubernetes + Helm | Running | `helm list -n taskboard` → `taskboard` deployed. 2 frontend + 2 backend + Postgres pods Running; ClusterIP Services; Ingress on an NLB; HPA `cpu: 2%/70%`; PVC Bound on gp3 |
| Argo CD | Synced | Application `taskboard` Synced/Healthy; a push to `main` rolled the backend to the new SHA with no manual step |
| M9 Observability | Running | kube-prometheus-stack; ServiceMonitor targets for both backend pods `up`; Grafana dashboard `TaskBoard API` provisioned from the chart |
| M10 Docs | Done except video | README, docs/, `demo/presentation.pptx` and `demo/slides.pdf` (12 slides). Video still to record |

## Problems found on real AWS, and the fixes

| Problem | Fix |
| --- | --- |
| Organization SCP denies EC2/EKS outside `ap-southeast-2` | Region moved to `ap-southeast-2` everywhere |
| AWS Free plan rejects `t3.medium` (not free-tier eligible) | Node group uses `m7i-flex.large` (2 vCPU, 8 GiB, 29 pods) |
| EKS 1.35 has no Amazon Linux 2 AMIs | `ami_type = "AL2023_x86_64_STANDARD"` |
| PVC would stay Pending without a CSI driver | `aws-ebs-csi-driver` add-on, node-role policy, default `gp3` StorageClass |
| SCP denies `iam:CreateOpenIDConnectProvider` | `enable_irsa = false` |
| ServiceMonitor CRD missing at app install | Install kube-prometheus-stack before the app |
| Grafana doubled `taskboard_tasks_by_status` (reported per pod) | Dashboard uses `max` across pods |

## Cost and destroy

About $0.40/hour while the stack is up (EKS control plane, NAT gateway, 2 nodes, NLB, EBS). Tear down after recording:

```bash
bash scripts/aws/99-destroy.sh
```

The Terraform state is in `terraform/terraform.tfstate` (gitignored) on the machine that applied it.
