const pptxgen = require('pptxgenjs');
const React = require('react');
const RDS = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const si = require('react-icons/si');
const { applyTheme } = require(process.env.APPLY_THEME || './apply_theme.js');

const THEME = { name: 'TaskBoard Ops', headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1: '1B2430', lt1: 'FFFFFF', dk2: '0F3D3E', lt2: 'EEF4F3', accent1: '0F8B8D', accent2: 'F2A541',
    accent3: '3D5A80', accent4: 'C8553D', accent5: '6C8EAD', accent6: '7FB685', hlink: '0F8B8D', folHlink: '3D5A80' } };
const H = { ink: '1B2430', deep: '0F3D3E', teal: '0F8B8D', amber: 'F2A541', mist: 'EEF4F3', white: 'FFFFFF', slate: '5B6770', red: 'C8553D', navy: '3D5A80' };

async function icon(Comp, color, size = 256) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: '#' + color, size }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = 'Ramneek Singh';
  pres.title = 'TaskBoard DevOps Capstone';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  pres.defineSlideMaster({ title: 'DARK', background: { color: H.deep },
    objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 1.5, w: 8.8, h: 1.4, fontSize: 40, bold: true, color: C.background1, fontFace: 'Cambria', valign: 'bottom' }, text: '' } }] });
  pres.defineSlideMaster({ title: 'CONTENT', background: { color: H.white },
    objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 9, h: 0.75, fontSize: 30, bold: true, color: C.text1, fontFace: 'Cambria', valign: 'middle', align: 'left', margin: 0 }, text: '' } }],
    slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: '5B6770', fontFace: 'Calibri' } });

  const body = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontFace: 'Calibri', fontSize: 14, color: H.ink, margin: 0, valign: 'top' }, o));
  const card = (s, x, y, w, h, fill) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || H.mist }, line: { color: fill || H.mist } });
  const circleIcon = async (s, Comp, x, y, d, bg, fg) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg } });
    s.addImage({ data: await icon(Comp, fg), x: x + d * 0.25, y: y + d * 0.25, w: d * 0.5, h: d * 0.5 });
  };

  // 1 Title
  pres.addSection({ title: 'Intro' });
  let s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Intro' });
  s.addText('TaskBoard: from git commit to a monitored Kubernetes cluster', { placeholder: 'title' });
  body(s, 'DevOps Final Capstone  ·  Ramneek Singh  ·  October 2026', { x: 0.6, y: 3.05, w: 8.8, h: 0.4, fontSize: 18, color: 'CFE3E1' });
  body(s, 'React · FastAPI · PostgreSQL · GitHub Actions · Trivy · GHCR · Terraform · EKS · Helm · Argo CD · Prometheus · Grafana', { x: 0.6, y: 3.6, w: 8.8, h: 0.6, fontSize: 13, color: H.amber, italic: true });
  s.addNotes('Introduce the project: a task management app used as the vehicle to show a full delivery pipeline from a laptop to a monitored EKS cluster.');

  // 2 Overview with stats
  pres.addSection({ title: 'Project' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Project' });
  s.addText('A task board shipped like a production service', { placeholder: 'title' });
  body(s, [
    { text: 'Teams create tasks, set priority and assignee, and move them through TODO → IN PROGRESS → DONE.', options: { breakLine: true } },
    { text: 'Every change travels the same path: tests, image build, security scan, registry, GitOps deploy, metrics.', options: {} },
  ], { x: 0.5, y: 1.25, w: 9, h: 0.9, fontSize: 15, paraSpaceAfter: 6 });
  const stats = [['6', 'task REST endpoints\n+ health, ready, metrics'], ['17', 'automated tests\n13 pytest + 4 frontend'], ['2', 'container images\nscanned and SHA-tagged'], ['59', 'AWS resources\ncreated by Terraform']];
  stats.forEach(([n, l], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 2.45, 2.05, 2.3);
    body(s, n, { x: x + 0.2, y: 2.6, w: 1.7, h: 1.0, fontSize: 54, bold: true, color: H.teal, fontFace: 'Cambria' });
    body(s, l, { x: x + 0.2, y: 3.65, w: 1.75, h: 0.95, fontSize: 13, color: H.slate });
  });

  // 3 Tech stack
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Project' });
  s.addText('Tech stack', { placeholder: 'title' });
  const stack = [
    [si.SiReact, 'Application', 'React + Vite UI on Nginx (non-root), FastAPI, SQLAlchemy, Alembic, PostgreSQL 16'],
    [si.SiPytest, 'Quality', 'pytest on SQLite, Node test runner, Compose healthchecks'],
    [si.SiGithubactions, 'CI/CD', 'GitHub Actions, Trivy image gate, GHCR with commit-SHA tags'],
    [si.SiTerraform, 'Infrastructure', 'Terraform AWS VPC and EKS modules, region ap-southeast-2'],
    [si.SiKubernetes, 'Platform', 'EKS 1.35, Helm chart, ingress-nginx, HPA, Metrics Server, Argo CD'],
    [si.SiPrometheus, 'Observability', 'kube-prometheus-stack: Prometheus Operator, ServiceMonitor, Grafana'],
  ];
  for (let i = 0; i < stack.length; i++) {
    const [ic, h, d] = stack[i];
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 1.3 + row * 1.3;
    await circleIcon(s, ic, x, y, 0.75, H.teal, H.white);
    body(s, h, { x: x + 0.95, y: y, w: 3.4, h: 0.35, fontSize: 16, bold: true });
    body(s, d, { x: x + 0.95, y: y + 0.36, w: 3.4, h: 0.8, fontSize: 13, color: H.slate });
  }

  // 4 Architecture
  pres.addSection({ title: 'Architecture' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Architecture' });
  s.addText('Architecture on AWS', { placeholder: 'title' });
  card(s, 2.15, 1.2, 7.35, 3.95, 'E3EEEC');
  body(s, 'EKS cluster · ap-southeast-2 · 2 × m7i-flex.large in private subnets', { x: 2.35, y: 1.28, w: 7, h: 0.3, fontSize: 12, bold: true, color: H.deep });
  const box = (x, y, w, h, t, fill, fc) => { card(s, x, y, w, h, fill); s.addText(t, { isTextBox: true, x, y, w, h, align: 'center', valign: 'middle', fontFace: 'Calibri', fontSize: 12, bold: true, color: fc || H.white, margin: 2 }); };
  const arrow = (x1, y1, x2, y2) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipV: y2 < y1, line: { color: H.slate, width: 1.5, endArrowType: 'triangle' } });
  box(0.5, 2.6, 1.3, 0.7, 'Browser', H.ink);
  box(2.4, 2.6, 1.5, 0.7, 'NLB +\ningress-nginx', H.navy);
  arrow(1.8, 2.95, 2.4, 2.95);
  box(4.4, 1.75, 1.6, 0.6, 'frontend ×2\nReact/Nginx', H.teal);
  box(4.4, 3.55, 1.6, 0.6, 'backend ×2–6\nFastAPI + HPA', H.teal);
  arrow(3.9, 2.8, 4.4, 2.05); arrow(3.9, 3.1, 4.4, 3.85);
  body(s, '/', { x: 4.0, y: 2.15, w: 0.4, h: 0.25, fontSize: 11, color: H.slate });
  body(s, '/api', { x: 3.95, y: 3.55, w: 0.45, h: 0.25, fontSize: 11, color: H.slate });
  box(6.5, 3.55, 1.4, 0.6, 'PostgreSQL\ngp3 EBS PVC', H.deep);
  arrow(6.0, 3.85, 6.5, 3.85);
  box(6.5, 4.4, 1.4, 0.55, 'Prometheus', H.red);
  box(8.15, 4.4, 1.2, 0.55, 'Grafana', H.amber, H.ink);
  arrow(5.2, 4.15, 6.5, 4.65); arrow(7.9, 4.67, 8.15, 4.67);
  box(6.5, 1.75, 1.4, 0.6, 'Argo CD', 'E96D4A');
  box(8.15, 1.75, 1.2, 0.6, 'GitHub\nmain', H.ink);
  arrow(8.15, 2.05, 7.9, 2.05); arrow(6.5, 2.2, 6.0, 3.6);
  body(s, 'scrapes /metrics', { x: 5.45, y: 4.55, w: 1.05, h: 0.4, fontSize: 10, color: H.slate });
  body(s, 'syncs chart', { x: 6.25, y: 2.55, w: 1.1, h: 0.3, fontSize: 10, color: H.slate });
  body(s, 'Terraform owns the VPC, NAT gateway, EKS and node group. Helm owns the workload. Argo CD keeps the cluster equal to git.', { x: 0.5, y: 3.55, w: 1.55, h: 1.6, fontSize: 11, color: H.slate });

  // 5 CI/CD
  pres.addSection({ title: 'Delivery' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Delivery' });
  s.addText('CI/CD: every push to main becomes a deploy', { placeholder: 'title' });
  const steps = [['Push', 'git push to main'], ['Test', 'pytest, npm test,\nVite build'], ['Build', 'backend and\nfrontend images'], ['Scan', 'Trivy HIGH/CRITICAL\nfails the job'], ['Publish', 'GHCR tagged with\nthe commit SHA'], ['GitOps', 'bot writes SHA to\nvalues-eks.yaml'], ['Sync', 'Argo CD rolls\nthe cluster']];
  steps.forEach(([t, d], i) => {
    const x = 0.5 + i * 1.3;
    s.addShape(pres.shapes.CHEVRON, { x, y: 1.5, w: 1.25, h: 0.75, fill: { color: i === 3 ? H.red : (i >= 5 ? H.amber : H.teal) }, line: { color: H.white } });
    s.addText(t, { isTextBox: true, x: x + 0.15, y: 1.5, w: 1.0, h: 0.75, align: 'center', valign: 'middle', fontFace: 'Calibri', fontSize: 13, bold: true, color: i >= 5 ? H.ink : H.white, margin: 0 });
    body(s, d, { x, y: 2.4, w: 1.25, h: 0.8, fontSize: 11, color: H.slate, align: 'center' });
  });
  card(s, 0.5, 3.45, 9, 1.55);
  body(s, [
    { text: 'Quality gates stop bad code before an image exists. ', options: { bold: true } },
    { text: 'Tests run first; a failure means no image, no scan, no tag.', options: { breakLine: true } },
    { text: 'Images are immutable. ', options: { bold: true } },
    { text: 'ghcr.io/ramneek3/taskboard/backend:<sha>; never latest, so every pod traces to a commit.', options: { breakLine: true } },
    { text: 'Deploy is a git commit. ', options: { bold: true } },
    { text: 'No cluster credentials live in GitHub; Argo CD pulls the change.', options: {} },
  ], { x: 0.75, y: 3.6, w: 8.5, h: 1.3, fontSize: 13, paraSpaceAfter: 4 });

  // 6 Security
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Delivery' });
  s.addText('DevSecOps controls', { placeholder: 'title' });
  const sec = [
    [fa.FaShieldAlt, 'Trivy gate', 'Both images scanned in CI; HIGH or CRITICAL with a fix fails the build. Current scans are clean after moving to Alpine bases and patched FastAPI/Starlette.'],
    [fa.FaUserLock, 'Non-root containers', 'API runs as uid 10001, Nginx as 101, Postgres as 70. runAsNonRoot is enforced in the pod spec.'],
    [fa.FaKey, 'No secrets in git', 'DB and Grafana passwords are generated into Kubernetes Secrets at install time. .env, tfvars and tfstate are gitignored.'],
    [fa.FaLock, 'Least exposure', 'Nodes in private subnets behind a NAT gateway; only the load balancer is public. EKS secrets are KMS-encrypted.'],
  ];
  for (let i = 0; i < sec.length; i++) {
    const [ic, h, d] = sec[i]; const x = 0.5 + (i % 2) * 4.6, y = 1.25 + Math.floor(i / 2) * 1.95;
    card(s, x, y, 4.35, 1.75);
    await circleIcon(s, ic, x + 0.25, y + 0.25, 0.65, H.deep, H.amber);
    body(s, h, { x: x + 1.1, y: y + 0.25, w: 3.05, h: 0.35, fontSize: 16, bold: true });
    body(s, d, { x: x + 1.1, y: y + 0.62, w: 3.05, h: 1.05, fontSize: 12, color: H.slate });
  }

  // 7 Terraform
  pres.addSection({ title: 'Platform' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Platform' });
  s.addText('Terraform: AWS network and EKS as code', { placeholder: 'title' });
  card(s, 0.5, 1.2, 5.3, 3.95, 'E3EEEC');
  body(s, 'VPC 10.20.0.0/16 · ap-southeast-2', { x: 0.7, y: 1.3, w: 5, h: 0.3, fontSize: 12, bold: true, color: H.deep });
  ['AZ a', 'AZ b'].forEach((az, i) => {
    const x = 0.75 + i * 2.55;
    body(s, az, { x, y: 1.7, w: 2.3, h: 0.25, fontSize: 11, color: H.slate });
    box(x, 2.0, 2.3, 0.75, 'public subnet\nNLB' + (i === 0 ? ' · NAT gateway' : ''), H.navy);
    box(x, 3.0, 2.3, 1.05, 'private subnet\nEKS node (m7i-flex.large)', H.teal);
  });
  box(0.75, 4.3, 4.85, 0.6, 'EKS 1.35 control plane · AL2023 nodes · EBS CSI add-on', H.deep);
  body(s, [
    { text: 'terraform init → plan → apply → destroy', options: { bold: true, breakLine: true } },
    { text: 'Community modules: terraform-aws-modules/vpc 5.8.1 and eks 20.37.1', options: { bullet: true, breakLine: true } },
    { text: 'Plan: 59 resources to add, 0 to change', options: { bullet: true, breakLine: true } },
    { text: 'Region pinned to ap-southeast-2: the account\'s organization SCP denies every other region', options: { bullet: true, breakLine: true } },
    { text: 'tfvars.example committed; real tfvars and state never are', options: { bullet: true, breakLine: true } },
    { text: 'About $0.40/hour while up; destroyed after the demo', options: { bullet: true } },
  ], { x: 6.1, y: 1.3, w: 3.4, h: 3.8, fontSize: 13, paraSpaceAfter: 6 });

  // 8 Kubernetes + Helm + Argo
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Platform' });
  s.addText('Kubernetes, Helm and Argo CD', { placeholder: 'title' });
  const k8s = [['Deployments', 'frontend ×2, backend ×2 with startup, readiness (/ready) and liveness (/health) probes'], ['Services', 'ClusterIP for frontend, backend and Postgres'], ['Ingress', 'ingress-nginx on an AWS NLB: / → frontend, /api → backend'], ['HPA', 'backend 2–6 replicas at 70% CPU, fed by Metrics Server'], ['Storage', 'Postgres on a 5 GiB encrypted gp3 PVC'], ['Monitoring', 'ServiceMonitor + Grafana dashboard ConfigMap in the chart']];
  k8s.forEach(([h, d], i) => {
    const y = 1.2 + i * 0.66;
    s.addShape(pres.shapes.OVAL, { x: 0.5, y: y + 0.08, w: 0.32, h: 0.32, fill: { color: H.teal }, line: { color: H.teal } });
    body(s, h, { x: 0.95, y, w: 1.5, h: 0.5, fontSize: 14, bold: true, valign: 'middle' });
    body(s, d, { x: 2.45, y, w: 3.5, h: 0.55, fontSize: 12, color: H.slate, valign: 'middle' });
  });
  card(s, 6.25, 1.2, 3.25, 3.95, H.deep);
  body(s, 'GitOps with Argo CD', { x: 6.5, y: 1.4, w: 2.8, h: 0.4, fontSize: 17, bold: true, color: H.white, fontFace: 'Cambria' });
  body(s, [
    { text: 'Application taskboard watches helm/taskboard on main with values-eks.yaml', options: { bullet: true, breakLine: true } },
    { text: 'Automated sync with prune and self-heal', options: { bullet: true, breakLine: true } },
    { text: 'helm upgrade --install for the first release; Argo CD keeps it in sync afterwards', options: { bullet: true } },
  ], { x: 6.5, y: 1.9, w: 2.8, h: 3.1, fontSize: 13, color: 'D9ECEA', paraSpaceAfter: 8 });

  // 9 Observability
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Platform' });
  s.addText('Observability: Prometheus and Grafana', { placeholder: 'title' });
  box(0.5, 1.5, 2.0, 0.8, 'FastAPI\n/metrics', H.teal);
  box(3.2, 1.5, 2.0, 0.8, 'ServiceMonitor\n15s scrape', H.navy);
  box(5.9, 1.5, 1.6, 0.8, 'Prometheus', H.red);
  box(7.9, 1.5, 1.6, 0.8, 'Grafana', H.amber, H.ink);
  arrow(2.5, 1.9, 3.2, 1.9); arrow(5.2, 1.9, 5.9, 1.9); arrow(7.5, 1.9, 7.9, 1.9);
  const panels = [['Traffic', 'Requests per second, by status code'], ['Errors', 'Rate of 5xx responses from the API'], ['Latency', 'p50 and p95 request duration'], ['Business', 'Tasks by status; created, updated and deleted per second']];
  panels.forEach(([h, d], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 2.8, 2.05, 1.9);
    body(s, h, { x: x + 0.2, y: 2.95, w: 1.7, h: 0.35, fontSize: 16, bold: true, color: H.deep });
    body(s, d, { x: x + 0.2, y: 3.35, w: 1.7, h: 1.25, fontSize: 12, color: H.slate });
  });
  body(s, 'Dashboard "TaskBoard API" ships inside the Helm chart, so Grafana picks it up as soon as the release is installed.', { x: 0.5, y: 4.85, w: 9, h: 0.35, fontSize: 12, italic: true, color: H.slate });

  // 10 Troubleshooting
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Platform' });
  s.addText('Troubleshooting drills', { placeholder: 'title' });
  const tr = [['ImagePullBackOff', 'troubleshooting/broken-image.yaml references a tag that does not exist.', 'kubectl describe pod → Events show "manifest unknown" → fix the image tag.'], ['Service with no endpoints', 'troubleshooting/broken-service.yaml selects a label no pod has.', 'kubectl get endpoints is empty → compare selector with pod labels → fix the selector.']];
  for (let i = 0; i < tr.length; i++) {
    const [h, a, b] = tr[i]; const x = 0.5 + i * 4.6;
    card(s, x, 1.25, 4.35, 3.8);
    await circleIcon(s, fa.FaBug, x + 0.25, 1.45, 0.65, H.red, H.white);
    body(s, h, { x: x + 1.1, y: 1.55, w: 3.1, h: 0.45, fontSize: 17, bold: true });
    body(s, 'Break', { x: x + 0.3, y: 2.35, w: 3.8, h: 0.3, fontSize: 12, bold: true, color: H.red });
    body(s, a, { x: x + 0.3, y: 2.65, w: 3.8, h: 0.75, fontSize: 13, color: H.slate });
    body(s, 'Diagnose and fix', { x: x + 0.3, y: 3.5, w: 3.8, h: 0.3, fontSize: 12, bold: true, color: H.teal });
    body(s, b, { x: x + 0.3, y: 3.8, w: 3.8, h: 1.0, fontSize: 13, color: H.slate });
  }

  // 11 Learnings
  pres.addSection({ title: 'Close' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Close' });
  s.addText('Key learnings', { placeholder: 'title' });
  const ls = [
    ['Read the platform, not the tutorial', 'EKS 1.35 ships no Amazon Linux 2 node images; the node group had to move to AL2023.'],
    ['Storage is not free on EKS', 'Without the EBS CSI add-on and a gp3 StorageClass, the Postgres PVC stays Pending forever.'],
    ['Org guardrails win', 'The org SCP allows only ap-southeast-2 and blocks OIDC providers; the Free plan rejects t3.medium, so nodes run m7i-flex.large.'],
    ['Tokens have scopes', 'GITHUB_TOKEN can only publish packages under the repository name, so images live at ghcr.io/<owner>/<repo>/<image>.'],
    ['Liveness ≠ readiness', '/health stays cheap; /ready checks the database so traffic only reaches pods that can serve it.'],
    ['Destroy is part of the plan', 'Load balancers and volumes created by Kubernetes must go before terraform destroy can delete the VPC.'],
  ];
  ls.forEach(([h, d], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.2 + Math.floor(i / 2) * 1.32;
    body(s, String(i + 1).padStart(2, '0'), { x, y, w: 0.6, h: 0.5, fontSize: 24, bold: true, color: H.amber, fontFace: 'Cambria' });
    body(s, h, { x: x + 0.65, y, w: 3.7, h: 0.35, fontSize: 15, bold: true });
    body(s, d, { x: x + 0.65, y: y + 0.36, w: 3.7, h: 0.85, fontSize: 12, color: H.slate });
  });

  // 12 Close
  s = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Close' });
  s.addText('Thank you', { placeholder: 'title' });
  body(s, 'github.com/ramneek3/taskboard', { x: 0.6, y: 3.05, w: 8.8, h: 0.4, fontSize: 20, color: H.amber });
  body(s, 'Live walkthrough next: codebase → CI run → Terraform → Argo CD → kubectl → Prometheus → Grafana', { x: 0.6, y: 3.6, w: 8.8, h: 0.6, fontSize: 14, color: 'CFE3E1' });

  await pres.writeFile({ fileName: 'presentation.pptx' });
  await applyTheme('presentation.pptx', THEME);
  console.log('ok');
})().catch(e => { console.error(e); process.exit(1); });
