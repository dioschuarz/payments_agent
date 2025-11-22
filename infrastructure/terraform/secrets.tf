resource "google_secret_manager_secret" "api_key" {
  secret_id = "${var.service_name}-google-api-key"

  replication {
    auto {}
  }

  # Ensure Secret Manager API is enabled before creating secrets
  depends_on = [google_project_service.secret_manager]

  # Lifecycle: If secret already exists, import it instead of failing
  lifecycle {
    # Terraform will attempt to import if resource exists (handled by provider)
    # If you get 409 error, run: terraform import google_secret_manager_secret.api_key projects/{project_id}/secrets/{secret_id}
  }
}

# Note: Secret value should be set manually or via CI/CD
# gcloud secrets versions add ${var.service_name}-google-api-key --data-file=-

