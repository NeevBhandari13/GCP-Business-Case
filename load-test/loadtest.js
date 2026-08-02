/**
 * Blissey Health Analytics — k6 load test
 *
 * Simulates the bursty batch-ingestion pattern from John's email:
 * ~40 clinics uploading on their own schedules → genuine burst-then-idle,
 * not a synthetic e-commerce spike.
 *
 * Stages:
 *   0:00–1:00  warm-up       (5 VUs  — a handful of early-morning clinics)
 *   1:00–3:00  burst 1       (40 VUs — all 40 clinics uploading mid-morning)
 *   3:00–5:00  idle          (2 VUs  — quiet period between batches)
 *   5:00–6:00  ramp-up       (80 VUs — doubling: 40→80 clinics onboarded)
 *   6:00–8:00  burst 2       (80 VUs — watch Autopilot scale with zero node work)
 *   8:00–9:00  cool-down     (0 VUs  — pods drain back toward minimum)
 *
 * Usage:
 *   BASE_URL=http://<loadbalancer-ip> k6 run loadtest.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const errorRate = new Rate("errors");
const scoringDuration = new Trend("scoring_duration", true);

export const options = {
  stages: [
    { duration: "1m",  target: 5  },  // warm-up
    { duration: "2m",  target: 40 },  // burst 1: 40 clinics
    { duration: "2m",  target: 2  },  // idle
    { duration: "1m",  target: 80 },  // ramp to 80 clinics
    { duration: "2m",  target: 80 },  // burst 2: 80 clinics
    { duration: "1m",  target: 0  },  // cool-down
  ],
  // k6 exits with a non-zero code if either is breached
  thresholds: {
    // 95th-percentile response time under 500ms at full load
    scoring_duration: ["p(95)<500"],
    // Error rate below 1%
    errors: ["rate<0.01"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";

// Synthetic patient data.
function randomPatient() {
  const clinicId = `clinic-${Math.floor(Math.random() * 80) + 1}`;
  return {
    patient_id:         `p-${Math.random().toString(36).slice(2, 10)}`,
    clinic_id:          clinicId,
    age:                Math.floor(Math.random() * 80) + 18,
    num_conditions:     Math.floor(Math.random() * 8),
    num_medications:    Math.floor(Math.random() * 12),
    last_visit_days_ago: Math.floor(Math.random() * 300),
  };
}

export default function () {
  const payload = JSON.stringify(randomPatient());
  const params  = { headers: { "Content-Type": "application/json" } };

  const res = http.post(`${BASE_URL}/score`, payload, params);

  const ok = check(res, {
    "status 200":            (r) => r.status === 200,
    "has risk_score":        (r) => JSON.parse(r.body).risk_score !== undefined,
    "risk_tier is valid":    (r) => ["low", "medium", "high"].includes(
                                     JSON.parse(r.body).risk_tier),
  });

  errorRate.add(!ok);
  scoringDuration.add(res.timings.duration);

  // Small pause between requests per VU — each VU represents one clinic
  // worker. Keeps the pattern realistic.
  sleep(Math.random() * 0.5 + 0.1);
}
