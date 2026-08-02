# Blissey Health Analytics — GKE Autopilot POC

## Purpose of this project
This is a portfolio proof-of-concept built to prepare for a **Google Cloud Customer
Engineer (CE)** job application/interview. The goal is not to build a real product —
it's to demonstrate CE-relevant skills through a small, working, well-narrated POC:
technical build quality, business framing, objection handling, and presentation-ready
architecture.

The POC responds to a fictional but realistic inbound customer scenario (full text in
`docs/scenario.md`). Everything built should trace back to a requirement in that email.

**When picking this up in Claude Code: read `docs/scenario.md` and `docs/plan.md`
first**, before writing or changing any code. They contain the "why" behind every
design decision below.

---

## The fictional customer (for narrative consistency)

- **Company:** Blissey Health Analytics — ingests claims + patient-outcomes data
  from ~40 regional clinics, runs ML models to flag high-risk patients for care teams.
- **Contact:** John Smith, VP of Engineering.
- **Pain points:** self-managed on-prem Kubernetes cluster, ~1/3 of 2 backend
  engineers' time spent on node patching/upgrades, a 14-hour outage in March from a
  control-plane failure, Privacy Act / APP-aligned audit pressure, AWS (EKS + Fargate) already
  pitching them, Q4 renewal/budget decision looming.
- **Ask:** architecture proposal + working POC + cost predictability numbers + data
  security story + direct handling of migration risk / vendor lock-in objections.
  20 min technical presentation + 10 min Q&A, engineers in the room will push back.

Full text: `docs/scenario.md`.

---

## Solution summary

**Platform: GKE Autopilot** (region-based, not zonal) is the centerpiece — it directly
answers "why not just run GKE ourselves again," which is the customer's core objection
to any Kubernetes-based proposal.

### Why Autopilot (the pitch's crux)
- No node management — Google handles provisioning, OS patching, CVE remediation
  (this is literally the 30% of engineer time the customer says they're losing).
- Built-in security posture by default (Shielded GKE Nodes, Workload Identity,
  restricted privileged workloads) — not reliant on a departed contractor's config.
- Pay-per-pod-resource billing — cost tracks actual usage, feeds the CFO cost ask.
- SRE-grade control plane SLA — direct answer to the March 14-hour outage.
- Honest trade-off to name proactively: less low-level node control, some
  DaemonSet/privileged workload patterns restricted.

### Full target architecture (not all of it gets built in the one-day POC — see scope note)
```
Clinics (simulated data feed)
   → Cloud Pub/Sub (ingestion buffer)              [diagrammed, not built]
   → Dataflow (transform, de-identify)              [diagrammed, not built]
   → BigQuery (claims + outcomes warehouse)          [optional, seed w/ script]
   → GKE Autopilot workloads:
        - risk-scoring service (FastAPI, toy model) [BUILT]
        - dashboard API                              [diagrammed, not built]
   → Cloud SQL (MySQL) for app state              [optional in POC]
   → Cloud Load Balancing + Cloud Armor              [diagrammed, not built]
   → Cloud Monitoring/Logging                        [BUILT — dashboard + 1 alert]
   → Secret Manager for credentials                  [BUILT]
   → Workload Identity for pod → GCP service auth    [BUILT]
```
Everything intended to sit behind a VPC-SC perimeter, private GKE nodes, no public
IPs on backend services (VPC-SC itself is diagrammed/described, not fully built,
given the one-day time box).

### What gets actually built vs. described in slides
**Build (real, working):**
- Terraform: VPC/subnet, GKE Autopilot cluster, Artifact Registry, service account +
  IAM bindings, Secret Manager secret resource.
- FastAPI "risk-scoring" service (toy model, synthetic input → fake risk score),
  containerized, pushed to Artifact Registry.
- Kubernetes manifests: Deployment, Service, HPA.
- Workload Identity wiring: pod-level GCP auth, least-privilege IAM
  (`roles/secretmanager.secretAccessor` scoped to one secret, minimal
  Cloud SQL/BigQuery role if those are included).
- Secret Manager holding the one credential the app needs (DB password or dummy
  API key) — no plaintext secrets in YAML or env vars.
- Load test (`k6` or `hey`) that visibly triggers HPA autoscaling — screen-recorded
  as a backup in case live demo fails during the actual interview.
- Cloud Monitoring: one dashboard (request latency + error rate, or pod CPU/memory
  if the app doesn't expose custom metrics) + one alert policy (e.g. error rate > 5%).

**Describe only (diagram + talking points, not built):**
- Pub/Sub ingestion, Dataflow pipeline, dashboard frontend/API, Cloud Load
  Balancing + Cloud Armor, full VPC-SC perimeter, CMEK, audit logging, CI/CD
  (Cloud Build) — mentioned as a documented next step, not demoed.

This split is intentional and should be *stated explicitly* in the presentation —
knowing what to build vs. what to responsibly describe is itself part of what's
being evaluated for a CE role.

---

## Skills this POC is meant to demonstrate
1. **Infrastructure as code** — Terraform for the infra layer (cluster, network,
   IAM, secrets), plain Kubernetes YAML for the app/workload layer. This
   infra-vs-workload split in tooling is itself a talking point (realistic pattern
   many orgs use).
2. **Security posture** — Workload Identity (no static keys), Secret Manager
   (no plaintext credentials), least-privilege IAM.
3. **Operability / observability** — Cloud Monitoring dashboard + alert policy,
   framed as answering "how do we know it's healthy after migration."
4. **Cost fluency** — a real comparison table (self-managed on-prem vs.
   self-managed GKE vs. GKE Autopilot) built from the GCP pricing calculator,
   not estimated from memory.
5. **Business framing / objection handling** — explicit responses to "we tried
   Kubernetes and it was a nightmare," migration risk, and vendor lock-in,
   delivered as part of the presentation, not dodged.
6. **Discovery-style thinking** — the presentation opens by reframing the
   customer's stated pain in their own words before pitching anything.
7. **Roadmap/program thinking** — closing slide: Phase 1 (this POC) → Phase 2
   (pipeline + full Privacy Act / APP controls) → Phase 3 (production cutover).

Deliberately deferred (named as gaps, not hidden): CI/CD pipeline, full VPC-SC,
CMEK, audit logging, Dataflow pipeline.

---

## Repo structure (target)
```
Blissey-poc/
├── CLAUDE.md                  (this file)
├── docs/
│   ├── scenario.md            (the inbound customer email, verbatim)
│   ├── plan.md                (one-day build timeline + task breakdown)
│   └── presentation-outline.md (20+10 min structure, objection-handling notes)
├── terraform/
│   ├── main.tf                (VPC, subnet, GKE Autopilot cluster)
│   ├── artifact-registry.tf
│   ├── iam.tf                 (service accounts, Workload Identity bindings)
│   ├── secret-manager.tf
│   └── variables.tf / outputs.tf
├── app/
│   ├── main.py                (FastAPI risk-scoring service)
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── load-test/
│   └── loadtest.js            (k6 script)
└── monitoring/
    └── dashboard.json         (Cloud Monitoring dashboard definition, if scripted)
```
This structure doesn't exist yet in this project — build it fresh, following
`docs/plan.md`'s task order.

---

## Constraints to respect while building
- One-day time budget — favor "working and simple" over "complete." Cut scope per
  `docs/plan.md`'s stated priority order if time runs short, don't silently expand
  scope.
- No real health data, ever — synthetic/dummy data only. This is itself a talking
  point in the presentation (data minimization awareness), not just a shortcut.
- Never hardcode credentials — Secret Manager + Workload Identity from the start,
  not bolted on later.
- Keep the FastAPI service simple — a toy model is fine and expected; the point is
  the platform/infra story, not ML sophistication.
- GKE Autopilot has some restrictions vs. standard GKE (e.g. certain privileged
  workload / DaemonSet patterns) — don't design the app in a way that fights this;
  if a restriction is hit, that itself becomes a documented talking point for
  objection handling, not a blocker to work around with standard GKE.

## Open decisions / things to confirm when resuming
- Whether to include Cloud SQL at all in the one-day scope, or mock app state
  in-memory (email mentions Cloud SQL for dashboard state, but dashboard itself is
  out of scope for the build — confirm whether risk-scoring service needs any
  persistent state at all before building Cloud SQL infra).
- Whether to script the Cloud Monitoring dashboard as code (`monitoring/dashboard.json`
  via `gcloud monitoring dashboards create`) or just build it manually in console and
  screenshot it — pick whichever is faster given remaining time.
- GCP project ID / billing account to use — not yet specified.
