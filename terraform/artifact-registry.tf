resource "google_artifact_registry_repository" "app" {
  repository_id = "blissey-app"
  location      = var.region
  format        = "DOCKER"
  description   = "Container images for Blissey risk-scoring service"

  depends_on = [google_project_service.apis]
}
