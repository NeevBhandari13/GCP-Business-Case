#!/usr/bin/env bash
# Apply the Cloud Monitoring dashboard and alert policy.
# Run after `terraform apply` and cluster is reachable.
#
# Usage: PROJECT_ID=blissey-health ./monitoring/deploy.sh

set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID before running this script}"

echo "Deploying dashboard..."
gcloud monitoring dashboards create \
  --config-from-file=monitoring/dashboard.json \
  --project="$PROJECT_ID"

echo "Deploying alert policy..."
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/alert-policy.json \
  --project="$PROJECT_ID"

echo "Done. View at: https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
