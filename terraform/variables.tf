variable "project_id" {
  description = "GCP project ID"
  default     = "blissey-health"
}

variable "region" {
  description = "Primary region — australia-southeast2 for Privacy Act / APP data residency"
  default     = "australia-southeast2"
}

variable "cluster_name" {
  default = "blissey-autopilot"
}

variable "db_instance_name" {
  default = "blissey-postgres"
}

variable "db_name" {
  default = "blissey"
}

variable "db_user" {
  default = "blissey_app"
}
