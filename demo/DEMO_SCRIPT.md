# Demo video script (about 12–15 minutes)

Order follows SUBMISSION.md. Record with macOS screen recording (Cmd+Shift+5 → Record Entire Screen, with microphone).

## Before you press record (5 minutes)

1. Open **Terminal** and run:
   ```bash
   source ~/Desktop/taskboard/scripts/aws/demo-env.sh
   terraform -chdir=terraform init -input=false >/dev/null && echo "terraform ready"
   bash scripts/aws/08-open-dashboards.sh
   ```
   The last command prints the TaskBoard URL and the Argo CD and Grafana passwords. Keep that window open; it holds the port-forwards.
2. Open a **second Terminal tab** (Cmd+T) and run `source ~/Desktop/taskboard/scripts/aws/demo-env.sh` again. Use this tab on camera.
3. Log in once in your browser so the video does not show passwords: Argo CD at http://localhost:8080 and Grafana at http://localhost:3001 (user `admin`).
4. Open these browser tabs in order:
   - `demo/slides.pdf` (or open `demo/presentation.pptx` in Keynote/PowerPoint)
   - https://github.com/ramneek3/taskboard
   - https://github.com/ramneek3/taskboard/actions
   - https://github.com/ramneek3?tab=packages
   - The TaskBoard URL printed by step 1
   - AWS Console → VPC (Sydney) and AWS Console → EKS → `taskboard-eks`
   - http://localhost:8080/applications/argocd/taskboard
   - http://localhost:9090/targets?search=taskboard
   - http://localhost:3001/d/taskboard-api
5. Optional, for busy Grafana panels: `bash scripts/aws/09-load-test.sh` a minute before recording.

## 1. Slides (3–4 min)

Walk through the 12 slides: overview, stack, architecture, CI/CD flow, security, Terraform, Kubernetes/Argo CD, observability, troubleshooting, learnings.

## 2. Codebase (2 min)

On GitHub, show: `backend/app/main.py` (endpoints), `backend/tests/`, `backend/alembic/versions/`, `frontend/src/`, both `Dockerfile`s, `.github/workflows/ci-cd.yml`, `terraform/main.tf`, `helm/taskboard/`, `gitops/argocd/application.yaml`.

## 3. Application (1 min)

Open the TaskBoard URL (this is the Ingress / NLB). Create a task, move it to In Progress. Then in Terminal:
```bash
curl -s http://$(kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')/api/tasks | head -c 300; echo
kubectl exec deploy/taskboard-postgres -- psql -U taskboard -d taskboard -c 'select id, title, status, priority from tasks;'
```

## 4. CI/CD: trigger a push (3 min, mostly waiting)

On GitHub, open `frontend/index.html` → pencil (Edit) → change `<title>TaskBoard</title>` to `<title>TaskBoard · EKS</title>` → **Commit changes** to `main` with a message like "Show the deployment target in the page title".
Open **Actions**: show jobs *Test and build frontend* → *Build images and Trivy gate* (open the Trivy step log) → *Publish immutable images to GHCR* → *Update GitOps image tags for Argo CD*.
While it runs, continue with Terraform. Afterwards show the GHCR package page with the new SHA tag, and the bot commit "Deploy <sha> to EKS through Argo CD".

## 5. Terraform (2 min)

```bash
cat logs/terraform-plan.txt | grep -E "will be created|Plan:" | tail -15
terraform -chdir=terraform plan -input=false
```
The live plan should say **No changes**: the infrastructure matches the code. Then show AWS Console: VPC `taskboard-eks-vpc` with 4 subnets and the NAT gateway, and EKS cluster `taskboard-eks` with its node group.

## 6. Argo CD (1 min)

Show application `taskboard` **Synced / Healthy** and the resource tree. Point at the revision: it matches the bot commit from step 4. Click **History and rollback** to show the previous deploys.

## 7. Kubernetes and Helm (1–2 min)

```bash
kubectl get nodes
kubectl get pods -n taskboard -o wide
kubectl get svc,ingress,hpa,pvc -n taskboard
helm list -n taskboard
kubectl -n taskboard get deploy taskboard-backend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
```
The image tag should be the SHA of the commit you just pushed.

## 8. Prometheus and Grafana (1–2 min)

Prometheus Targets: `serviceMonitor/taskboard/taskboard-backend` with both endpoints **UP**. Grafana: dashboard **TaskBoard API**: request rate, latency, tasks by status (should match the board).

## 9. Troubleshooting (2 min, optional but scores well)

```bash
kubectl apply -f troubleshooting/namespace.yaml -f troubleshooting/broken-image.yaml -f troubleshooting/broken-service.yaml
kubectl -n taskboard-troubleshoot get pods          # ImagePullBackOff
kubectl -n taskboard-troubleshoot describe pod -l app=broken-image | tail -8
kubectl -n taskboard-troubleshoot get endpoints     # broken-service has none
kubectl delete namespace taskboard-troubleshoot
```

## After recording

Save the video as `demo/taskboard-demo.mp4` and tell Claude. Then the cluster gets destroyed with `bash scripts/aws/99-destroy.sh`.
