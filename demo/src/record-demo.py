"""Records the TaskBoard demo as separate clips (one Playwright context per segment).

Usage: python3 rec.py <segment> [<segment> ...]
Clips land in clips/<segment>.webm. Terminal segments run the real commands at
record time and replay their captured output in a terminal-styled page.
"""
import asyncio, json, os, re, shutil, subprocess, sys, html, time, glob
from playwright.async_api import async_playwright

ROOT = "/tmp/claude-0/video"
CLIPS = f"{ROOT}/clips"
REPO = "/home/claude/taskboard"
W, H = 1280, 720
PROXY = os.environ.get("HTTPS_PROXY")
ENV = dict(os.environ)
for k in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]:
    ENV.pop(k, None)
ENV.update(AWS_REGION="ap-southeast-2", AWS_DEFAULT_REGION="ap-southeast-2",
           PATH=f"{os.path.expanduser('~/bin')}:{ENV['PATH']}", AWS_CA_BUNDLE="/root/.ccr/ca-bundle.crt",
           TF_DATA_DIR=os.path.expanduser("~/.tfdata"), TERM="dumb", NO_COLOR="1")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def sh(cmd, cwd=REPO, timeout=300):
    p = subprocess.run(["bash", "-c", cmd], cwd=cwd, env=ENV, capture_output=True, text=True, timeout=timeout)
    out = ANSI.sub("", (p.stdout or "") + (p.stderr or ""))
    return out.rstrip("\n")


CAPTION_JS = """
(([text, section]) => {
  let bar = document.getElementById('__cap');
  if (!bar) {
    bar = document.createElement('div'); bar.id = '__cap';
    bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:2147483647;background:rgba(15,61,62,0.94);color:#fff;font:600 21px/1.35 Calibri,Carlito,Arial,sans-serif;padding:14px 28px 16px 28px;box-shadow:0 -2px 12px rgba(0,0,0,.25)';
    document.documentElement.appendChild(bar);
    const tag = document.createElement('div'); tag.id = '__sec';
    tag.style.cssText = 'position:fixed;top:12px;right:14px;z-index:2147483647;background:#F2A541;color:#1B2430;font:700 14px Calibri,Carlito,Arial,sans-serif;padding:5px 12px;border-radius:14px;letter-spacing:.5px';
    document.documentElement.appendChild(tag);
  }
  bar.textContent = text;
  document.getElementById('__sec').textContent = section;
  bar.style.display = text ? 'block' : 'none';
})
"""


class Seg:
    def __init__(self, browser, name, section):
        self.browser, self.name, self.section = browser, name, section

    async def __aenter__(self):
        self.ctx = await self.browser.new_context(viewport={"width": W, "height": H}, record_video_dir=f"{CLIPS}/tmp_{self.name}",
                                                  record_video_size={"width": W, "height": H}, ignore_https_errors=False, locale="en-US", timezone_id="Asia/Kolkata")
        self.page = await self.ctx.new_page()
        await self.page.set_content("<html><body style='margin:0;background:#0d1b1e'></body></html>")
        self.cap_text = ""
        return self

    async def __aexit__(self, *a):
        path = await self.page.video.path() if self.page.video else None
        await self.ctx.close()
        if path:
            shutil.move(path, f"{CLIPS}/{self.name}.webm")
            shutil.rmtree(f"{CLIPS}/tmp_{self.name}", ignore_errors=True)
        print("clip", self.name)

    async def cap(self, text):
        self.cap_text = text
        try:
            await self.page.evaluate(CAPTION_JS, [text, self.section])
        except Exception:
            pass

    async def go(self, url, text=None, wait="domcontentloaded", settle=1.5):
        await self.page.goto(url, wait_until=wait, timeout=90000)
        await asyncio.sleep(settle)
        await self.cap(text if text is not None else self.cap_text)

    async def hold(self, s):
        # Re-assert the caption while holding (SPAs may re-render the body).
        end = time.time() + s
        while time.time() < end:
            await self.cap(self.cap_text)
            await asyncio.sleep(min(1.0, max(0.05, end - time.time())))

    async def scroll(self, px, steps=6, pause=0.5):
        for _ in range(steps):
            await self.page.mouse.wheel(0, px / steps)
            await asyncio.sleep(pause)
        await self.cap(self.cap_text)


TERM_HTML = """<!doctype html><html><head><meta charset=utf-8><style>
html,body{margin:0;height:100%;background:#0d1b1e}
#t{box-sizing:border-box;height:100%;padding:26px 30px 110px 30px;overflow:hidden;color:#d8e6e3;font:15px/1.42 'DejaVu Sans Mono',Menlo,monospace;white-space:pre}
.p{color:#7fd1c7}.c{color:#ffffff;font-weight:bold}.o{color:#c9d6d3}.h{color:#F2A541}
#bar{position:fixed;top:0;left:0;right:0;height:26px;background:#1f3337;color:#9fb8b3;font:12px 'DejaVu Sans';text-align:center;line-height:26px}
</style></head><body><div id=bar>Terminal — taskboard</div><div id=t></div></body></html>"""

TERM_JS = """
async ([steps]) => {
  const t = document.getElementById('t'); t.style.paddingTop='38px';
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (const s of steps) {
    if (s.clear) { t.innerHTML=''; }
    if (s.note) { const n=document.createElement('span'); n.className='h'; n.textContent='# '+s.note+'\\n'; t.appendChild(n); await sleep(500); }
    const p = document.createElement('span'); p.className='p'; p.textContent='taskboard $ '; t.appendChild(p);
    const c = document.createElement('span'); c.className='c'; t.appendChild(c);
    for (const ch of s.cmd) { c.textContent += ch; t.scrollTop = t.scrollHeight; await sleep(28); }
    t.appendChild(document.createTextNode('\\n')); await sleep(350);
    const lines = s.out ? s.out.split('\\n') : [];
    for (const l of lines) { const o=document.createElement('span'); o.className='o'; o.textContent=l+'\\n'; t.appendChild(o); t.scrollTop = t.scrollHeight; await sleep(lines.length > 40 ? 12 : 35); }
    await sleep(s.hold || Math.min(9000, 2200 + lines.length * 160));
  }
}
"""


def clip_lines(out, maxw=128, maxl=60):
    ls = [l if len(l) <= maxw else l[:maxw - 1] + "…" for l in out.split("\n")]
    if len(ls) > maxl:
        ls = ls[:maxl] + [f"… ({len(ls) - maxl} more lines)"]
    return "\n".join(ls)


def prep(steps):
    data = []
    for s in steps:
        out = s.get("out")
        if out is None:
            out = sh(s.get("run", s["cmd"]), timeout=s.get("timeout", 300))
        if s.get("filter"):
            out = s["filter"](out)
        data.append(dict(_prepped=True, cmd=s["cmd"], out=clip_lines(out, maxl=s.get("maxl", 60)), note=s.get("note"), hold=s.get("hold"), clear=s.get("clear")))
    return data


async def terminal(seg, steps, caption):
    data = steps if steps and "out" in steps[0] and "run" not in steps[0] and steps[0].get("_prepped") else prep(steps)
    await seg.page.set_content(TERM_HTML)
    await seg.cap(caption)
    if isinstance(caption, list):
        pass
    await seg.page.evaluate(TERM_JS, [data])
    await asyncio.sleep(0.5)
    return data


async def card(seg, title, sub, secs=5, dark=True):
    await seg.page.set_content(f"""<!doctype html><html><body style="margin:0;height:100vh;display:flex;flex-direction:column;justify-content:center;
      padding:0 90px;box-sizing:border-box;background:{'#0F3D3E' if dark else '#fff'};font-family:Cambria,Caladea,serif">
      <div style="color:{'#fff' if dark else '#1B2430'};font-size:50px;font-weight:bold">{html.escape(title)}</div>
      <div style="color:#F2A541;font:22px Calibri,Carlito,sans-serif;margin-top:18px;white-space:pre-line">{html.escape(sub)}</div></body></html>""")
    await seg.cap("")
    await asyncio.sleep(secs)


# ---------------------------------------------------------------- segments
LB = None


def lb():
    global LB
    if not LB:
        LB = sh("kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'")
    return LB


async def seg_intro(b):
    async with Seg(b, "00_intro", "INTRO") as s:
        await card(s, "TaskBoard · DevOps Capstone", "Ramneek Singh  ·  October 2026\n\nSlides first, then a live walkthrough of the running system:\ncodebase → CI/CD → Terraform → Argo CD → Kubernetes → Prometheus → Grafana\n\nEvery screen after the slides is a live system recorded on 21 October 2026.", 9)


async def seg_slides(b):
    async with Seg(b, "01_slides", "SLIDES") as s:
        imgs = sorted(glob.glob("/tmp/claude-0/deck/s-*.png"))
        holds = [8, 12, 12, 16, 15, 12, 15, 14, 12, 11, 14, 6]
        for i, img in enumerate(imgs):
            await s.page.set_content(f"<html><body style='margin:0;background:#fff'><img src='data:image/png;base64,{__import__('base64').b64encode(open(img,'rb').read()).decode()}' style='width:1280px;height:720px;display:block;object-fit:contain'></body></html>")
            await asyncio.sleep(holds[i] if i < len(holds) else 10)


async def seg_code(b):
    gh = "https://github.com/ramneek3/taskboard"
    async with Seg(b, "02_code", "CODEBASE") as s:
        await s.go(gh, "Repository on GitHub: backend/ (FastAPI), frontend/ (React), terraform/, helm/, gitops/, monitoring/, troubleshooting/, demo/")
        await s.hold(4); await s.scroll(500, 5, 0.6); await s.hold(3)
        files = [
            ("backend/app/main.py", "backend/app/main.py: /health, /ready (checks the DB), /metrics, and the task CRUD endpoints", 1400),
            ("backend/tests/test_api.py", "backend/tests/: pytest against an in-memory SQLite database, so tests never touch production data", 1000),
            ("backend/alembic/versions/0001_create_tasks.py", "Alembic migration 0001 creates the tasks table; the API never calls create_all", 500),
            ("frontend/Dockerfile", "frontend/Dockerfile: multi-stage build, Node builds the app, nginx-unprivileged serves it as a non-root user", 300),
            ("backend/Dockerfile", "backend/Dockerfile: Python Alpine image, runs as uid 10001, entrypoint runs migrations then Uvicorn", 500),
            (".github/workflows/ci-cd.yml", "CI/CD workflow: test → build images → Trivy gate → publish to GHCR by commit SHA → GitOps tag bump", 2600),
            ("terraform/main.tf", "terraform/main.tf: VPC with public and private subnets plus NAT gateway, and the EKS cluster with its node group", 1200),
            ("helm/taskboard/values-eks.yaml", "helm/taskboard/values-eks.yaml: the image tag that CI rewrites on every push and Argo CD deploys", 200),
            ("gitops/argocd/application.yaml", "Argo CD Application: watches helm/taskboard on main, automated sync with prune and self-heal", 200),
        ]
        for path, text, px in files:
            await s.go(f"{gh}/blob/main/{path}", text, settle=2.5)
            await s.hold(3)
            if px > 300:
                await s.page.mouse.move(640, 420)
                await s.scroll(px, 8, 0.55)
            await s.hold(2.5)
        await s.go(f"{gh}/tree/main/helm/taskboard/templates", "Helm chart templates: Deployments, Services, Ingress, HPA, Postgres + PVC, ServiceMonitor, Grafana dashboard", settle=2.5)
        await s.hold(6)


async def seg_app(b):
    async with Seg(b, "03_app", "APPLICATION") as s:
        await s.go("http://127.0.0.1:8081/", "TaskBoard served by the cluster through the ingress-nginx controller: / goes to the React frontend, /api to FastAPI", settle=3)
        await s.hold(5)
        await s.page.get_by_role("button").filter(has_text=re.compile("New task", re.I)).first.click()
        await s.cap("Creating a task in the UI. The browser only calls /api; the Ingress routes it to the backend Service")
        await asyncio.sleep(1.2)
        await s.page.locator("input[name=title]").type("Record the capstone demo", delay=60)
        await s.page.locator("textarea[name=description]").type("Walk through CI/CD, Terraform, Argo CD, Kubernetes and monitoring", delay=25)
        await s.page.locator("select[name=priority]").select_option("HIGH")
        await s.page.locator("input[name=assignee]").fill("")
        await s.page.locator("input[name=assignee]").type("Ramneek", delay=60)
        await asyncio.sleep(1)
        await s.page.locator("button[type=submit]").click()
        await s.hold(4)
        await s.cap("Advance status moves the task TODO → IN PROGRESS, which is a PUT /api/tasks/{id}")
        await s.page.locator("button[title='Advance status']").first.click()
        await s.hold(5)
        await s.page.get_by_role("tab").nth(2).click() if await s.page.get_by_role("tab").count() > 2 else None
        await s.hold(3)
        lbh = lb()
        await terminal(s, [
            dict(note="The same API through the public AWS Network Load Balancer, called from a throwaway pod", cmd=f"kubectl run nlb-check --rm -i --restart=Never --image=curlimages/curl:8.10.1 -q -- curl -s http://{lbh[:28]}…/api/stats",
                 run=f"kubectl -n taskboard run nlb-check --rm -i --restart=Never --image=curlimages/curl:8.10.1 -q -- curl -s http://{lbh}/api/stats", hold=4000),
            dict(note="Rows stored in PostgreSQL (tasks table created by the Alembic migration)", cmd="kubectl -n taskboard exec deploy/taskboard-postgres -- psql -U taskboard -d taskboard -c 'select id, title, status, priority, assignee from tasks;'", hold=6000),
        ], "Live check: API through the AWS load balancer, then the PostgreSQL tasks table")


async def seg_ci_push(b):
    if True:
        steps = [
            dict(note="A small application change: show the deployment target in the page title", cmd="sed -i 's#<title>TaskBoard</title>#<title>TaskBoard · EKS</title>#' frontend/index.html && git diff --stat", hold=3000),
            dict(cmd="git commit -am 'Show the deployment target in the page title'", run="git -c user.name=Claude -c user.email=noreply@anthropic.com commit -qam 'Show the deployment target in the page title\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>' && git log --oneline -1", hold=2500),
            dict(cmd="git push origin main", run="git pull -q --rebase origin main && git push origin main 2>&1 | tail -3", hold=3000),
        ]
        d = prep(steps)
    async with Seg(b, "04a_ci_push", "CI/CD") as s:
        await terminal(s, d, "Trigger the pipeline: commit a change and push to main")
        await s.go("https://github.com/ramneek3/taskboard/actions", "GitHub Actions starts the TaskBoard CI run for this commit", settle=4)
        await s.hold(5)
        run = sh("sleep 5; gh run list -R ramneek3/taskboard -L 1 --json databaseId -q '.[0].databaseId'")
        open(f"{ROOT}/run_id", "w").write(run)
        await s.go(f"https://github.com/ramneek3/taskboard/actions/runs/{run}", "The run graph: tests first; images are built and scanned only if tests pass; publish and GitOps run only on main", settle=4)
        await s.hold(10)


async def seg_ci_done(b):
    run = open(f"{ROOT}/run_id").read().strip()
    jobs = json.loads(sh(f"gh run view {run} -R ramneek3/taskboard --json jobs -q '.jobs'"))
    jid = {j["name"]: j["databaseId"] for j in jobs}
    def log(job, pattern, n=14):
        return f"gh run view -R ramneek3/taskboard --job {jid[job]} --log | sed -E 's/^[^\\t]*\\t[^\\t]*\\t[0-9TZ:.-]+ //' | {pattern} | head -{n}"
    d = prep([
        dict(note="Job results for this run, read with the GitHub CLI", cmd=f"gh run view {run} -R ramneek3/taskboard", run=f"gh run view {run} -R ramneek3/taskboard | sed -n '1,22p'", hold=6000),
        dict(clear=True, note="Quality gate: pytest runs before any image is built (13 dots = 13 backend tests passed; then 4 frontend tests)", cmd=f"gh run view --job <test job> --log | grep -E '100%|# pass|# fail'", run=log("Test and build frontend", "grep -E '\\[100%\\]|^# (pass|fail)|^# tests'", 6), hold=4500),
        dict(note="Security gate: Trivy on both images, HIGH/CRITICAL, exit-code 1", cmd=f"gh run view --job <trivy job> --log | grep -A12 'Report Summary'", run=log("Build images and Trivy gate", "grep -E -A9 'Report Summary'", 26), hold=9000),
        dict(clear=True, note="Registry: images pushed to GHCR with the commit SHA as the tag", cmd=f"gh run view --job <publish job> --log | grep -E 'pushing manifest|naming to'", run=log("Publish immutable images to GHCR", "grep -E 'pushing manifest|naming to'", 6), hold=5000),
        dict(note="GitOps: the bot commits the new tag; Argo CD deploys it", cmd=f"gh run view --job <gitops job> --log | grep -E 'Deploy|main'", run=log("Update GitOps image tags for Argo CD", "grep -E 'Deploy [0-9a-f]{7}|-> main'", 4), hold=5000),
    ])
    tok = "TOKEN=$(curl -s 'https://ghcr.io/token?scope=repository:ramneek3/taskboard/backend:pull' | python3 -c 'import sys,json;print(json.load(sys.stdin)[\"token\"])')"
    sha = sh("git rev-parse HEAD~1 2>/dev/null; git log -1 --format=%H --grep='Show the deployment target'").split("\n")[-1]
    d2 = prep([dict(clear=True, cmd="curl -s -H \"Authorization: Bearer $TOKEN\" https://ghcr.io/v2/ramneek3/taskboard/backend/tags/list",
                    run=tok + "; curl -s -H \"Authorization: Bearer $TOKEN\" https://ghcr.io/v2/ramneek3/taskboard/backend/tags/list | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d[\"name\"]);[print(\"  \",t) for t in d[\"tags\"][-8:]]'", hold=4000),
               dict(cmd="git log -1 --format='%H %s'", hold=4500)])
    async with Seg(b, "04b_ci_done", "CI/CD") as s:
        await s.go(f"https://github.com/ramneek3/taskboard/actions/runs/{run}", "Pipeline finished: test, build + Trivy, publish to GHCR, GitOps tag bump, Terraform validate and Helm lint, all green", settle=4)
        await s.hold(9)
        await terminal(s, d, "The real job logs from this run: tests, Trivy scan summary, GHCR push by SHA, and the GitOps commit")
        await s.go("https://github.com/ramneek3?tab=packages&ecosystem=container", "GHCR packages: taskboard/backend and taskboard/frontend, published by the pipeline, public so EKS can pull them", settle=4)
        await s.hold(8)
        await terminal(s, d2, "Registry tags straight from ghcr.io: every tag is a full commit SHA; there is no 'latest'")
        await s.go("https://github.com/ramneek3/taskboard/commits/main", "Commit history: my change, then github-actions[bot] 'Deploy <sha> to EKS through Argo CD [skip ci]'", settle=4)
        await s.hold(9)


async def seg_terraform(b):
    if True:
        steps = [
            dict(note="The plan that built the stack (saved from the first terraform plan)", cmd="grep -E 'will be created|^Plan:' logs/terraform-plan.txt | sed -n '1,8p;$p'",
                 run="sed 's/\\x1b\\[[0-9;]*m//g' logs/terraform-plan.txt | grep -E 'will be created|^Plan:' | sed 's/^ *//' | grep -E 'aws_vpc\\.|aws_subnet|aws_nat_gateway|aws_eks_cluster|aws_eks_node_group|aws_eks_addon|^Plan:'", hold=5000),
            dict(note="Live plan against AWS now: infrastructure matches the code", cmd="terraform -chdir=terraform plan -input=false -var-file=terraform.tfvars", run="terraform -chdir=terraform plan -input=false -var-file=terraform.tfvars -no-color 2>&1 | grep -vE 'Refreshing state|Reading|Read complete' | tail -6", timeout=400, hold=5000),
            dict(cmd="terraform -chdir=terraform output", run="terraform -chdir=terraform output -no-color", hold=4000, clear=True),
        ]
        d1 = prep(steps)
        steps2 = [
            dict(clear=True, note="AWS proof: the VPC and its subnets", cmd="aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC --query 'Subnets[].[Tags[?Key==`Name`]|[0].Value,CidrBlock,AvailabilityZone]' --output table",
                 run="VPC=$(terraform -chdir=terraform output -raw vpc_id); aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC --query 'Subnets[].[Tags[?Key==`Name`]|[0].Value,CidrBlock,AvailabilityZone]' --output table", hold=4000),
            dict(cmd="aws ec2 describe-nat-gateways --query 'NatGateways[?State==`available`].[NatGatewayId,State,VpcId]' --output table", hold=3000),
            dict(cmd="aws eks describe-cluster --name taskboard-eks --query 'cluster.{name:name,version:version,status:status,endpointPublic:resourcesVpcConfig.endpointPublicAccess}' --output table", hold=3500),
            dict(cmd="aws eks describe-nodegroup --cluster-name taskboard-eks --nodegroup-name $NG --query 'nodegroup.{status:status,type:instanceTypes[0],ami:amiType,desired:scalingConfig.desiredSize}' --output table",
                 run="NG=$(aws eks list-nodegroups --cluster-name taskboard-eks --query 'nodegroups[0]' --output text); aws eks describe-nodegroup --cluster-name taskboard-eks --nodegroup-name $NG --query 'nodegroup.{status:status,type:instanceTypes[0],ami:amiType,desired:scalingConfig.desiredSize}' --output table", hold=5000),
        ]
        d2 = prep(steps2)
    async with Seg(b, "05_terraform", "TERRAFORM") as s:
        await terminal(s, d1, "Terraform: Infrastructure as Code for the AWS VPC and EKS cluster in ap-southeast-2 (Sydney)")
        await terminal(s, d2, "Live AWS API output: VPC with 2 public + 2 private subnets, NAT gateway, EKS 1.35 cluster and its node group")


async def seg_argocd(b):
    async with Seg(b, "06_argocd", "ARGO CD") as s:
        await s.go("http://127.0.0.1:8080/applications", "Argo CD: the taskboard Application is Synced and Healthy", settle=5)
        await s.hold(6)
        await s.go("http://127.0.0.1:8080/applications/argocd/taskboard?view=tree&resource=", "Resource tree that Argo CD manages from git: Deployments, ReplicaSets, Pods, Services, Ingress, HPA, PVC, ServiceMonitor", settle=6)
        await s.hold(12)
        rev = sh("kubectl -n argocd get application taskboard -o jsonpath='{.status.sync.revision}'")[:7]
        await s.cap(f"Synced to revision {rev}: the bot commit from the pipeline. Nobody ran kubectl or helm for this deploy")
        await s.hold(8)
        await s.go("http://127.0.0.1:8080/applications/argocd/taskboard?view=tree&resource=&rollback=0", "History: every pipeline run shows up as a deploy that can be rolled back", settle=5)
        await s.hold(9)


async def seg_k8s(b):
    if True:
        steps = [
            dict(cmd="kubectl get nodes -o wide", run="kubectl get nodes -o wide | awk '{print $1,$2,$4,$5,$6}' | column -t", hold=3500),
            dict(cmd="kubectl get pods -n taskboard -o wide", run="kubectl get pods -n taskboard -o wide | awk '{print $1,$2,$3,$4,$5,$7}' | column -t", hold=4500),
            dict(clear=True, cmd="kubectl get svc,ingress,hpa,pvc -n taskboard", run="kubectl get svc,ingress,hpa,pvc -n taskboard 2>&1 | cut -c1-128", hold=6000),
            dict(cmd="helm list -n taskboard", hold=3500),
            dict(clear=True, note="The running image is the commit SHA from the push in this video", cmd="kubectl -n taskboard get deploy taskboard-backend -o jsonpath='{.spec.template.spec.containers[0].image}'", hold=3000),
            dict(cmd="git log --oneline -3", hold=4500),
        ]
        d = prep(steps)
    async with Seg(b, "07_k8s", "KUBERNETES + HELM") as s:
        await terminal(s, d, "Kubernetes on EKS: 2 nodes, frontend and backend at 2 replicas, ClusterIP Services, Ingress on an NLB, HPA, gp3 volume")


async def seg_prom(b):
    async with Seg(b, "08_prometheus", "PROMETHEUS") as s:
        await s.go("http://127.0.0.1:9090/targets?search=taskboard", "Prometheus Targets: the ServiceMonitor for taskboard-backend, both pods UP and scraped every 15s", settle=4)
        await s.hold(10)
        await s.go("http://127.0.0.1:9090/query?g0.expr=sum%20by%20(handler)%20(rate(http_requests_total%7Bnamespace%3D%22taskboard%22%7D%5B2m%5D))&g0.tab=graph&g0.range_input=30m", "PromQL: request rate per endpoint from the FastAPI /metrics instrumentation", settle=5)
        await s.hold(10)


async def seg_grafana(b):
    async with Seg(b, "09_grafana", "GRAFANA") as s:
        await s.go("http://127.0.0.1:3001/d/taskboard-api?orgId=1&from=now-30m&to=now&refresh=10s&kiosk", "Grafana dashboard TaskBoard API (shipped in the Helm chart): live request rate, errors, latency, tasks by status", settle=7)
        await s.hold(12)
        await s.scroll(600, 6, 0.7)
        await s.hold(10)


async def seg_trouble(b):
    if True:
        steps = [
            dict(note="Break two things on purpose in a separate namespace", cmd="kubectl apply -f troubleshooting/namespace.yaml -f troubleshooting/broken-image.yaml -f troubleshooting/broken-service.yaml", run="kubectl apply -f troubleshooting/namespace.yaml -f troubleshooting/broken-image.yaml -f troubleshooting/broken-service.yaml; sleep 25", hold=2500),
            dict(cmd="kubectl -n taskboard-troubleshoot get pods", hold=3500),
            dict(note="Symptom 1: ImagePullBackOff. describe shows why", cmd="kubectl -n taskboard-troubleshoot describe pod -l app=broken-image | grep -E 'Image:|Failed|Back-off' | head -5", run="kubectl -n taskboard-troubleshoot describe pod -l app=broken-image | grep -E 'Image:|Failed|Back-off' | head -5 | cut -c1-128", hold=6000),
            dict(clear=True, note="Symptom 2: a Service with no endpoints. Its selector matches no pod labels", cmd="kubectl -n taskboard-troubleshoot get endpoints", hold=3000),
            dict(cmd="kubectl -n taskboard-troubleshoot get svc broken-service -o jsonpath='{.spec.selector}'; echo", hold=2500),
            dict(cmd="kubectl -n taskboard-troubleshoot get pods --show-labels", run="kubectl -n taskboard-troubleshoot get pods --show-labels | awk '{print $1,$3,$NF}' | column -t", hold=4000),
            dict(note="Fix: point the image at a real tag and the selector at real labels. Clean up", cmd="kubectl delete namespace taskboard-troubleshoot", hold=3000),
        ]
        d = prep(steps)
    async with Seg(b, "10_troubleshoot", "TROUBLESHOOTING") as s:
        await terminal(s, d, "Troubleshooting drill: ImagePullBackOff (wrong tag) and a Service whose selector matches no pods")


async def seg_outro(b):
    async with Seg(b, "11_outro", "") as s:
        await card(s, "Thank you", "github.com/ramneek3/taskboard\n\nApplication → Git → CI → Docker → Trivy → GHCR → Terraform → EKS → Helm → Ingress → HPA → Argo CD → Prometheus → Grafana", 8)


SEGS = {k[4:]: v for k, v in globals().items() if k.startswith("seg_")}


async def main(names):
    os.makedirs(CLIPS, exist_ok=True)
    async with async_playwright() as p:
        bp = await p.chromium.launch(proxy={"server": PROXY})
        bl = await p.chromium.launch()
        local = {"app", "argocd", "prom", "grafana", "intro", "slides", "outro", "terraform", "k8s", "trouble"}
        for n in names:
            await SEGS[n](bl if n in local else bp)
        await bp.close(); await bl.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
