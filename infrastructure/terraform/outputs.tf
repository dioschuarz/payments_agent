output "service_url" {
  description = "Cloud Run service URL (direct access - BLOCKED for security. Use custom domain instead)"
  value       = google_cloud_run_v2_service.service.uri
  sensitive   = false
}

output "custom_domain_url" {
  description = "Custom domain URL (if configured). This is the only way to access the service."
  value       = var.custom_domain != "" ? "https://${var.custom_domain}" : null
}

output "load_balancer_ip" {
  description = "Load Balancer IP address (configure DNS to point custom_domain to this IP)"
  value       = google_compute_global_address.cloud_run_ip.address
}

output "load_balancer_url" {
  description = "Load Balancer URL (protected by Cloud Armor) - Use custom domain instead if configured"
  value       = var.cloud_armor_enable_ssl || var.custom_domain != "" ? "https://${google_compute_global_address.cloud_run_ip.address}" : "http://${google_compute_global_address.cloud_run_ip.address}"
}

output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.service.name
}

output "secret_name" {
  description = "Secret Manager secret name"
  value       = google_secret_manager_secret.api_key.secret_id
}

output "ssl_certificate_name" {
  description = "Name of managed SSL certificate (if custom domain is configured). Check status in GCP Console (can take 10-60 min to provision)"
  value       = var.custom_domain != "" ? google_compute_managed_ssl_certificate.domain_cert[0].name : null
}

output "cloud_armor_policy_name" {
  description = "Cloud Armor security policy name"
  value       = google_compute_security_policy.armor_policy.name
}
