# Project Brief: Charicard.com Infrastructure Modernization

**From:** Charicard.com — VP of Engineering
**To:** Google Cloud Customer Engineering
**Re:** Request for architecture recommendation ahead of Q4 card drop season

---

## Who we are

Charicard.com is an online marketplace for buying, selling, and trading collectible cards — sports cards, trading card games, and limited "drop" releases. Sellers list inventory, buyers purchase individual cards or full lots, and we handle payment processing and order fulfillment tracking end to end. We've grown fast over the past two years, mostly by word of mouth in collector communities, and our engineering setup hasn't caught up with the business.

We're reaching out ahead of Q4 because we can't afford another repeat of what happened last November, and we want a real recommendation, not just reassurance.

## What we're currently running

I'll be straight with you about what this actually looks like today, because I think it matters for whatever you recommend:

- Everything runs on **one Compute Engine VM** — our application server and our MySQL database are on the same box.
- The app itself is a **single monolithic codebase**. Card inventory, order/checkout, and payment processing are all part of the same deployable unit — there's no separation between them at the infrastructure level.
- Our database is **just MySQL installed on that VM**. We have a cron job that dumps a backup to a bucket once a day. That's the extent of our disaster recovery plan.
- Deploys are **manual**. Someone on the team SSHes into the box, pulls the latest code, and restarts the process. If something breaks, we redeploy the last known-good commit by hand. We don't have a rollback button.
- There's **no load balancer and no autoscaling**. Traffic goes straight to the VM. If we need more capacity, someone manually resizes the instance, which means a restart.
- Because everything runs in the same process, our **payment handling code has no isolation** from the rest of the app. Our payment processor has flagged this in a security questionnaire we're now required to complete annually, and we don't currently have a great answer for it.
- We don't have a dedicated infrastructure or SRE team. Our engineers wear a lot of hats, and infrastructure has mostly been "whoever's free."

## Why we're reaching out now

Three things are converging and we need a plan before Q4:

**1. Drop-day traffic is breaking us.**
When we do a limited card drop — a hyped release where a set number of cards go live at a specific time — we see traffic spike 8-10x normal volume in the first few minutes. Last November, our checkout flow went down for 40 minutes during our biggest drop of the year. We lost sales, and worse, we lost trust with a community that talks to each other constantly. We cannot let that happen again this Q4.

**2. We're splitting the monolith and need a platform that supports it.**
Our engineering team has wanted to break inventory, checkout, and payments into separate services for over a year — mostly so we can scale and deploy them independently, since checkout is our highest-traffic component by far and payments is our most sensitive. We've been holding off partly because we don't have infrastructure that would actually support that split cleanly.

**3. Our payment processor is pushing us on security posture.**
The annual security questionnaire from our payment processor specifically asked about network segmentation between payment processing and other application components. Right now we don't have a good answer. We need this resolved before our next review, not just for this questionnaire but because it's clearly the right thing to do given what we handle.

## What we're asking for

We'd like a recommended architecture that:
- Can handle 8-10x traffic spikes automatically, without someone manually intervening in real time
- Supports us splitting into independent services (inventory, checkout, payments) without a full re-platform later
- Gives us real network isolation for our payment processing workload
- Doesn't require us to hire a dedicated platform/ops team we don't currently have and can't resource right now

We've heard about Kubernetes from a few peer companies but honestly don't have strong opinions on GKE vs. Cloud Run vs. anything else — we're looking to you for that recommendation, and we'd like to understand the reasoning, not just the answer, since we'll be living with this decision as we grow.

We'd like to see a proposal, ideally with a small proof-of-concept, before we commit to anything ahead of Q4.
