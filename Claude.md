# Project: Charicard.com GKE Modernization Demo

## Context

Full scenario context lives in `docs/`:
- `Business Case.md` — the (fictional) client's request, written in their voice

Read both before doing architecture or code work — the technical choices below are deliberately justified against Charicard's three stated pain points (drop-day traffic spikes, planned service split, payment network isolation), and new work should trace back to one of them.

## Goal

This is a portfolio project for a Google Cloud Customer Engineer (Infrastructure/Platform specialization) interview. The deliverable is a working, demoable proof-of-concept — not a production system — so prioritize clarity and a clean demo story over completeness.

Target architecture:
- Small containerized CRUD app (checkout/order service) — can use or adapt a simple open-source Flask/Node app, this is a prop, don't over-invest in app logic
- Deployed to **GKE Autopilot**
- **Horizontal Pod Autoscaler** configured — this is the single most important artifact, needs to visibly scale under a load test
- **Cloud SQL** (Postgres or MySQL) as the backend, not local storage
- **NetworkPolicy** isolating the payments-relevant service/namespace
- **Workload Identity** for DB access (no static service account keys)
- **Secret Manager** for DB credentials
- **Terraform** (`main.tf`, kept simple — one file is fine) provisioning the GKE cluster, Cloud SQL instance, and networking
- One **Cloud Monitoring** dashboard (pod count, latency, error rate) and one alert policy

## Constraints

- Time budget: ~1-2 days of build time total. Skip anything that doesn't map to a pain point in the brief (no CI/CD pipeline needed, no multi-region, no service mesh — mention these as roadmap items instead of building them).
- Cost: tear down (`terraform destroy`) between work sessions to stay within free trial credit. Don't leave GKE clusters or Cloud SQL instances running idle.
- Code should be clean and commented — this repo may get reviewed as a work sample.

## Working style

- Ask before running anything that provisions billable GCP resources.
- When making an architecture decision not already covered in the docs, state the reasoning briefly (a sentence or two) rather than just doing it silently — the reasoning is as much the point of this project as the working code.
