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

# Grant Load Balancer access to Cloud Run (for Serverless NEG)
# Ensure project data is read before using project number
resource "google_project_iam_member" "load_balancer_cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${data.google_project.project.number}@cloudservices.gserviceaccount.com"

  depends_on = [data.google_project.project]
}

# Data source to get project number
# Ensure Cloud Resource Manager API is enabled before reading project
data "google_project" "project" {
  project_id = var.project_id

  depends_on = [google_project_service.cloud_resource_manager]
}

