resource "google_secret_manager_secret" "db_password" {
  secret_id = "blissey-db-password"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Placeholder version — replace with the real password before deploying.
# Using random_password here keeps the value out of source control and
# state is encrypted at rest in GCS backend.
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}
