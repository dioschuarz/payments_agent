resource "google_service_account" "cloud_run" {
  account_id   = "${var.service_name}-sa"
  display_name = "Cloud Run Service Account for ${var.service_name}"

  # Ensure IAM API is enabled before creating service account
  depends_on = [google_project_service.iam]
}

# Grant Secret Manager access
resource "google_secret_manager_secret_iam_member" "api_key_access" {
  secret_id = google_secret_manager_secret.api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Grant Cloud Run access
resource "google_project_iam_member" "cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Grant Artifact Registry access (cross-project for DEV to read from PRD registry)
# Only apply this if environment is "dev" (DEV needs to read from PRD Artifact Registry)
resource "google_artifact_registry_repository_iam_member" "artifact_registry_reader" {
  count      = var.environment == "dev" ? 1 : 0
  project    = replace(var.project_id, "-dev", "")  # Remove -dev suffix to get PRD project
  location   = var.region
  repository = "docker-repo"
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"

  # Ensure service account is created before granting permissions
  depends_on = [google_service_account.cloud_run]
}

# Grant Load Balancer access to Cloud Run (for Serverless NEG)
# NOTE: Cloud Services service account is created automatically by GCP when you use certain services
# If it doesn't exist yet, this will fail. In that case, create it manually or let GCP create it first.
# The service account is: PROJECT_NUMBER@cloudservices.gserviceaccount.com
# Uncomment after the service account exists or after first Compute Engine resource is created
# resource "google_project_iam_member" "load_balancer_cloud_run_invoker" {
#   project = var.project_id
#   role    = "roles/run.invoker"
#   member  = "serviceAccount:${data.google_project.project.number}@cloudservices.gserviceaccount.com"
#
#   depends_on = [data.google_project.project]
# }

# Data source to get project number
# Ensure Cloud Resource Manager API is enabled before reading project
data "google_project" "project" {
  project_id = var.project_id

  depends_on = [google_project_service.cloud_resource_manager]
}

