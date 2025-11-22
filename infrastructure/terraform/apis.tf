# Enable required Google Cloud APIs
# This ensures all necessary APIs are enabled for the project

resource "google_project_service" "secret_manager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"

  disable_dependent_services = false
}

resource "google_project_service" "cloud_run" {
  project = var.project_id
  service = "run.googleapis.com"

  disable_dependent_services = false
}

resource "google_project_service" "cloud_resource_manager" {
  project = var.project_id
  service = "cloudresourcemanager.googleapis.com"

  disable_dependent_services = false
}

resource "google_project_service" "iam" {
  project = var.project_id
  service = "iam.googleapis.com"

  disable_dependent_services = false
}

resource "google_project_service" "storage" {
  project = var.project_id
  service = "storage.googleapis.com"

  disable_dependent_services = false
}

resource "google_project_service" "compute" {
  project = var.project_id
  service = "compute.googleapis.com"

  disable_dependent_services = false
}

# Artifact Registry API - needed even for DEV (for cross-project image pulls)
resource "google_project_service" "artifact_registry" {
  project = var.project_id
  service = "artifactregistry.googleapis.com"

  disable_dependent_services = false
}

# Cloud DNS API - needed for automatic DNS record creation
resource "google_project_service" "dns" {
  count   = var.custom_domain != "" && var.dns_zone_name != "" ? 1 : 0
  project = var.dns_project_id != "" ? var.dns_project_id : var.project_id
  service = "dns.googleapis.com"

  disable_dependent_services = false
}

# Firestore API - needed for idempotency (anti-replay protection)
resource "google_project_service" "firestore" {
  project = var.project_id
  service = "firestore.googleapis.com"

  disable_dependent_services = false
}

