# Scenario: Inbound customer email

This is the fictional prompt the whole POC is designed against. Treat every design
decision as traceable back to a line in this email.

---

**From:** John Smith, VP of Engineering — Blissey Health Analytics
**To:** [You], Customer Engineer, Google Cloud
**Cc:** Dan Torres (Account Executive, Google Cloud)
**Subject:** Re: Follow-up from our call — architecture review before Q4 renewal decision

Hi,

Thanks for the intro call last week. As discussed, here's more context so your team can
put together something concrete before we meet again in three weeks.

**Who we are:** Blissey Health Analytics ingests claims and patient-outcomes data from
~40 regional clinics and runs ML models that flag high-risk patients for care teams.
Each clinic uploads its claims batch on its own schedule — some at 6am, some late at
night — so our risk-scoring pipeline sees genuinely bursty, uneven load throughout the
day, followed by long quiet periods in between. The dashboard itself is low, steady
traffic (doctors checking daily), but the scoring workload underneath is spiky and hard
to size for statically. We're also planning to onboard another 40+ clinics over the
next 12–18 months, which means ingestion volume is going to roughly double and we can't
predict exactly when each new clinic comes online.

**Current state:** Everything runs on a self-managed Kubernetes cluster on-prem,
provisioned two years ago by a contractor who's no longer with us. Our two backend
engineers spend roughly a third of their time just patching nodes, managing upgrades,
and troubleshooting cluster issues instead of building features. We had a control-plane
failure in March that took the dashboard down for 14 hours. We're also running a
self-managed MySQL instance on the same cluster — app state, a few lookup tables
the risk-scoring service reads at runtime, and some session data. Nobody's tested a
restore since the contractor left, and we have no documented backup retention policy,
which auditors flagged in the last review.

**Why we're evaluating cloud now:** Our board wants predictable costs and less
operational risk. We're also under increasing pressure to demonstrate Privacy Act / APP-aligned
security controls — our current setup makes that hard to prove to auditors. Budget
approval for a renewal decision happens in Q4, and honestly, AWS has already pitched us
on EKS + Fargate.

**What I need from you:**
1. A short architecture proposal showing how you'd re-platform our workload onto GCP,
   specifically addressing why we shouldn't just run vanilla GKE ourselves again
   (that's basically what got us into this mess).
2. A working proof-of-concept — doesn't need our real data, but should show autoscaling
   under load (specifically the kind of bursty batch-ingestion load we actually see, not
   just synthetic HTTP traffic), and ideally show how node/OS patching and upgrades stop
   being our team's problem.
3. Some way to show cost predictability — our CFO will ask for numbers, not vibes.
4. A plan for how we'd handle sensitive health data controls (even at a POC level, show you've thought about it — network policy, IAM, encryption, whatever's relevant).
5. Please keep the presentation to 10 minutes technical + Q&A. My engineers will be in the room and they will push back, especially on migration risk and lock-in. Don't dodge that — address it directly.

One more thing: our last vendor pitch was 80% slides and 20% substance. I'd rather see
something real, even if small.

Thanks — looking forward to it.

John

---

## Requirements checklist extracted from this email
- [ ] Architecture proposal, explicitly justifying platform vs. self-managed GKE
- [ ] Working POC — not just slides — showing autoscaling under bursty batch-ingestion load (not e-commerce spike fiction)
- [ ] Show node/OS patching stops being their team's problem
- [ ] Cost predictability numbers (real, not hand-waved)
- [ ] Privacy Act / APP-aligned controls story: network policy, IAM, encryption at minimum
- [ ] 20 min technical + 10 min Q&A format
- [ ] Direct handling of migration risk and vendor lock-in objections
- [ ] Substance over slides — bias toward something real and demoable
- [ ] Managed MySQL (Cloud SQL) — untested backups and no retention policy are audit gaps; show this gets solved
