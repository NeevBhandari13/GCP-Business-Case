# ---------------------------------------------------------------------------
# Private services access — required for Cloud SQL to get a private IP
# inside our VPC. This creates a VPC peering to Google's service network.
# ---------------------------------------------------------------------------

resource "google_compute_global_address" "private_service_range" {
  name          = "blissey-private-service-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 24
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_range.name]

  depends_on = [google_project_service.apis]
}

# ---------------------------------------------------------------------------
# Cloud SQL — MySQL 15, private IP only, no public endpoint
# ---------------------------------------------------------------------------

resource "google_sql_database_instance" "MySQL" {
  name             = var.db_instance_name
  database_version = "MYSQL_8_0"
  region           = var.region

  # Prevent accidental deletion during the demo
  deletion_protection = false

  settings {
    # db-f1-micro is the smallest tier — right-sized for a POC.
    # A production sizing conversation would start with actual query load.
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "app_db" {
  name     = var.db_name
  instance = google_sql_database_instance.MySQL.name
}

resource "google_sql_user" "app_user" {
  name     = var.db_user
  instance = google_sql_database_instance.MySQL.name
  password = random_password.db_password.result
}
