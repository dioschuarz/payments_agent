resource "google_secret_manager_secret" "api_key" {
  secret_id = "${var.service_name}-google-api-key"

  replication {
    automatic = true
  }
}

# Note: Secret value should be set manually or via CI/CD
# gcloud secrets versions add ${var.service_name}-google-api-key --data-file=-

