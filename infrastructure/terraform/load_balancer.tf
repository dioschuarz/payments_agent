# Load Balancer with Cloud Armor for Cloud Run

# Serverless NEG (Network Endpoint Group) for Cloud Run
resource "google_compute_region_network_endpoint_group" "cloud_run_neg" {
  name                  = "${var.service_name}-neg-${var.environment}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  cloud_run {
    service = google_cloud_run_v2_service.service.name
  }

  # Ensure Compute Engine API is enabled and Cloud Run service exists before creating NEG
  depends_on = [
    google_project_service.compute,
    google_cloud_run_v2_service.service # NEG needs Cloud Run service to exist first
  ]
}

# Backend Service
resource "google_compute_backend_service" "cloud_run_backend" {
  name                  = "${var.service_name}-backend-${var.environment}"
  description           = "Backend service for ${var.service_name} - ${var.environment}"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 30
  enable_cdn            = var.cloud_armor_enable_cdn
  load_balancing_scheme = "EXTERNAL_MANAGED"

  # Security policy (Cloud Armor)
  security_policy = google_compute_security_policy.armor_policy.id

  backend {
    group = google_compute_region_network_endpoint_group.cloud_run_neg.id
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }

  # Ensure Compute Engine API is enabled and all upstream resources exist before creating backend service
  depends_on = [
    google_project_service.compute,
    google_compute_security_policy.armor_policy,               # Security policy must exist
    google_compute_region_network_endpoint_group.cloud_run_neg # NEG must exist
  ]
}

# URL Map
resource "google_compute_url_map" "cloud_run_url_map" {
  name            = "${var.service_name}-urlmap-${var.environment}"
  description     = "URL map for ${var.service_name} - ${var.environment}"
  default_service = google_compute_backend_service.cloud_run_backend.id
}

# HTTP(S) Proxy
resource "google_compute_target_https_proxy" "cloud_run_https_proxy" {
  count            = var.cloud_armor_enable_ssl ? 1 : 0
  name             = "${var.service_name}-https-proxy-${var.environment}"
  url_map          = google_compute_url_map.cloud_run_url_map.id
  ssl_certificates = var.cloud_armor_ssl_certificate_id != "" ? [var.cloud_armor_ssl_certificate_id] : []
}

resource "google_compute_target_http_proxy" "cloud_run_http_proxy" {
  count   = var.cloud_armor_enable_ssl ? 0 : 1
  name    = "${var.service_name}-http-proxy-${var.environment}"
  url_map = google_compute_url_map.cloud_run_url_map.id
}

# Global Forwarding Rule (HTTP)
resource "google_compute_global_forwarding_rule" "cloud_run_http_forwarding" {
  count      = var.cloud_armor_enable_ssl ? 0 : 1
  name       = "${var.service_name}-http-forwarding-${var.environment}"
  target     = google_compute_target_http_proxy.cloud_run_http_proxy[0].id
  port_range = "80"
  ip_address = google_compute_global_address.cloud_run_ip.address
}

# Global Forwarding Rule (HTTPS)
resource "google_compute_global_forwarding_rule" "cloud_run_https_forwarding" {
  count      = var.cloud_armor_enable_ssl ? 1 : 0
  name       = "${var.service_name}-https-forwarding-${var.environment}"
  target     = google_compute_target_https_proxy.cloud_run_https_proxy[0].id
  port_range = "443"
  ip_address = google_compute_global_address.cloud_run_ip.address
}

# Global IP Address
resource "google_compute_global_address" "cloud_run_ip" {
  name         = "${var.service_name}-ip-${var.environment}"
  address_type = "EXTERNAL"
  ip_version   = "IPV4"

  # Ensure Compute Engine API is enabled before creating IP address
  depends_on = [google_project_service.compute]
}

