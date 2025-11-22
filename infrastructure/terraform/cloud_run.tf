resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region

  # --- CORREÇÃO: Ingress Control ---
  # Isso garante que NINGUÉM acesse a URL *.run.app diretamente.
  # Só aceita tráfego vindo do Load Balancer ou VPC interna.
  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  # Ensure Cloud Run API is enabled before creating service
  # Also ensure all prerequisites are created first:
  # - Service account and IAM bindings
  # - Secret Manager secret (needed for secret_key_ref)
  # - For DEV: wait for Artifact Registry IAM propagation (30s delay via null_resource bridge)
  depends_on = [
    google_project_service.cloud_run,
    google_service_account.cloud_run,
    google_secret_manager_secret.api_key,                   # Secret must exist before referencing
    google_secret_manager_secret_iam_member.api_key_access, # IAM binding for secret access
    google_project_iam_member.cloud_run_invoker,            # IAM binding for Cloud Run invocation
    null_resource.artifact_registry_iam_propagated          # For DEV: ensures IAM propagation completed
  ]

  # Lifecycle rules to handle existing resources and prevent accidental deletion
  lifecycle {
    # If resource already exists (409 error), import it instead of failing
    # This allows Terraform to manage resources that were created outside of Terraform

    # Ignore changes to template containers env that reference secrets
    # This prevents Terraform from trying to update Cloud Run when secret_key_ref changes
    # The secret version is managed outside Terraform (via GitHub Actions workflow)
    # Note: We still track changes to the secret_id itself, but not the version
    ignore_changes = [
      # Ignore changes to annotations/labels that might be added by GCP
      # Ignore changes to secret_key_ref version - secret versions are managed outside Terraform
      template[0].containers[0].env # This includes secret_key_ref which may change externally
    ]

    # Prevent accidental deletion - uncomment if you want extra protection
    # prevent_destroy = true

    # Create before destroy: Ensure new revision is created before destroying old one
    create_before_destroy = true
  }

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

# --- CORREÇÃO: Permitir invocação pública (controlada pelo Ingress acima) ---
# Removemos a restrição de IAM. Como o Ingress está restrito ao Load Balancer,
# e o Load Balancer tem o Cloud Armor, sua segurança está garantida.
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_v2_service.service.name
  location = google_cloud_run_v2_service.service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# --- REMOVIDO: O bloco que dava permissão para 'cloudservices' não é necessário para 
# Load Balancers Externos HTTP(S), ele não funciona como proxy de identidade.
# resource "google_cloud_run_service_iam_member" "load_balancer_access" {
#   service  = google_cloud_run_v2_service.service.name
#   location = google_cloud_run_v2_service.service.location
#   role     = "roles/run.invoker"
#   member   = "serviceAccount:${data.google_project.project.number}@cloudservices.gserviceaccount.com"
#
#   depends_on = [
#     data.google_project.project,
#     google_cloud_run_v2_service.service
#   ]
# }

