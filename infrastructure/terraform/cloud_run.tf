resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region

  # Ensure Cloud Run API is enabled before creating service
  depends_on = [google_project_service.cloud_run]

  template {
    containers {
      image = var.image

      env {
        name = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "LOG_LEVEL"
        value = var.log_level
      }

      env {
        name  = "SESSION_TTL_MINUTES"
        value = tostring(var.session_ttl_minutes)
      }

      env {
        name  = "CACHE_TTL_INTENT_HOURS"
        value = tostring(var.cache_ttl_intent_hours)
      }

      env {
        name  = "CACHE_TTL_BENEFICIARY_MINUTES"
        value = tostring(var.cache_ttl_beneficiary_minutes)
      }

      env {
        name  = "CACHE_TTL_VALIDATION_HOURS"
        value = tostring(var.cache_ttl_validation_hours)
      }

      env {
        name  = "GEMINI_MODEL"
        value = var.gemini_model
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }
    }

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    service_account = google_service_account.cloud_run.email
  }
}

# Allow unauthenticated access (for webhook)
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_v2_service.service.name
  location = google_cloud_run_v2_service.service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

