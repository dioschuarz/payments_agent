output "service_url" {
  description = "Cloud Run service URL (direct access - not protected by Cloud Armor)"
  value       = google_cloud_run_v2_service.service.uri
}

output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.service.name
}

output "secret_name" {
  description = "Secret Manager secret name"
  value       = google_secret_manager_secret.api_key.secret_id
}

output "load_balancer_ip" {
  description = "Load Balancer IP address (protected by Cloud Armor)"
  value       = google_compute_global_address.cloud_run_ip.address
}

output "load_balancer_url" {
  description = "Load Balancer URL (protected by Cloud Armor) - Use this for production traffic"
  value       = var.cloud_armor_enable_ssl ? "https://${google_compute_global_address.cloud_run_ip.address}" : "http://${google_compute_global_address.cloud_run_ip.address}"
}

output "cloud_armor_policy_name" {
  description = "Cloud Armor security policy name"
  value       = google_compute_security_policy.armor_policy.name
}

