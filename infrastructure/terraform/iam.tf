resource "google_service_account" "cloud_run" {
  account_id   = "${var.service_name}-sa"
  display_name = "Cloud Run Service Account for ${var.service_name}"

  # Ensure IAM API is enabled before creating service account
  depends_on = [google_project_service.iam]
}

# Grant Secret Manager access for Google API Key
resource "google_secret_manager_secret_iam_member" "api_key_access" {
  secret_id = google_secret_manager_secret.api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"

  # Ensure both secret and service account exist before granting access
  depends_on = [
    google_secret_manager_secret.api_key,
    google_service_account.cloud_run
  ]
}

# Grant Secret Manager access for Meta App Secret
resource "google_secret_manager_secret_iam_member" "meta_app_secret_access" {
  secret_id = google_secret_manager_secret.meta_app_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"

  # Ensure both secret and service account exist before granting access
  depends_on = [
    google_secret_manager_secret.meta_app_secret,
    google_service_account.cloud_run
  ]
}

# Grant Cloud Run access
resource "google_project_iam_member" "cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"

  # Ensure service account exists before granting IAM binding
  depends_on = [google_service_account.cloud_run]
}

# Grant Artifact Registry access (cross-project for DEV to read from PRD registry)
# Only apply this if environment is "dev" (DEV needs to read from PRD Artifact Registry)
resource "google_artifact_registry_repository_iam_member" "artifact_registry_reader" {
  count      = var.environment == "dev" ? 1 : 0
  project    = replace(var.project_id, "-dev", "") # Remove -dev suffix to get PRD project
  location   = var.region
  repository = "docker-repo"
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"

  # Ensure service account is created before granting permissions
  depends_on = [google_service_account.cloud_run]
}

# Grant Artifact Registry access to Cloud Run Service Agent (cross-project for DEV)
# The Cloud Run Service Agent (serverless-robot-prod) needs permission to pull images
# This is required for Cloud Run to deploy services using images from another project
# Only apply this if environment is "dev" (DEV needs to read from PRD Artifact Registry)
resource "google_artifact_registry_repository_iam_member" "artifact_registry_reader_service_agent" {
  count      = var.environment == "dev" ? 1 : 0
  project    = replace(var.project_id, "-dev", "") # Remove -dev suffix to get PRD project
  location   = var.region
  repository = "docker-repo"
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com"

  # Ensure project data source is available to get project number
  depends_on = [
    data.google_project.project,
    google_project_service.cloud_resource_manager
  ]
}

# Wait for IAM propagation (cross-project IAM can take time to propagate)
# This ensures the Artifact Registry IAM bindings are fully propagated before Cloud Run tries to pull the image
# Only for DEV environment (when Artifact Registry IAM is needed)
resource "time_sleep" "artifact_registry_iam_propagation" {
  count           = var.environment == "dev" ? 1 : 0
  create_duration = "30s" # Wait 30 seconds for IAM propagation

  depends_on = [
    google_artifact_registry_repository_iam_member.artifact_registry_reader[0],
    google_artifact_registry_repository_iam_member.artifact_registry_reader_service_agent[0]
  ]
}

# Null resource to ensure IAM propagation completes before Cloud Run creation
# This resource always exists and serves as a bridge for conditional dependencies
# For DEV: ensures time_sleep completes (IAM propagation); For PRD: no-op
resource "null_resource" "artifact_registry_iam_propagated" {
  # Always exists - ensures consistent dependency chain
  # For DEV: trigger includes time_sleep ID (when it exists), creating implicit dependency
  # For PRD: trigger only includes service account, completing immediately
  triggers = {
    service_account = google_service_account.cloud_run.email
    environment     = var.environment
    # For DEV: include time_sleep ID in trigger to create dependency (empty string if doesn't exist)
    # This ensures null_resource waits for time_sleep completion in DEV environment
    iam_propagation = var.environment == "dev" ? try(time_sleep.artifact_registry_iam_propagation[0].id, "") : ""
  }

  depends_on = [
    google_service_account.cloud_run
    # Note: time_sleep dependency is handled via triggers above for DEV
    # When environment is "dev", the trigger references time_sleep[0].id, creating implicit dependency
    # Terraform will evaluate the trigger expression and wait for time_sleep if it exists
    # For PRD: trigger evaluates to empty string, no dependency on time_sleep
  ]
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

