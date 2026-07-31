# ---------------------------------------------------------------------------
# Service account for the risk-scoring workload
# ---------------------------------------------------------------------------

resource "google_service_account" "risk_scorer" {
  account_id   = "risk-scorer"
  display_name = "Blissey Risk Scoring Service"
}

# Least-privilege: only the one secret it actually needs
resource "google_secret_manager_secret_iam_member" "risk_scorer_db_secret" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.risk_scorer.email}"
}

# Cloud SQL client access for the connection proxy / direct connection
resource "google_project_iam_member" "risk_scorer_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.risk_scorer.email}"
}

# ---------------------------------------------------------------------------
# Workload Identity binding — lets the Kubernetes SA impersonate the GCP SA,
# so the pod never needs a static key file.
# ---------------------------------------------------------------------------

resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.risk_scorer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[blissey/risk-scorer]"
}

# Allow Artifact Registry pulls from within the cluster
resource "google_project_iam_member" "cluster_ar_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.risk_scorer.email}"
}
