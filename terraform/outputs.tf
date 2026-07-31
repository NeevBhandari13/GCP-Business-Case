output "cluster_name" {
  value = google_container_cluster.autopilot.name
}

output "cluster_location" {
  value = google_container_cluster.autopilot.location
}

output "artifact_registry_repo" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app.repository_id}"
}

output "risk_scorer_service_account" {
  value = google_service_account.risk_scorer.email
}

output "db_secret_id" {
  value = google_secret_manager_secret.db_password.secret_id
}
