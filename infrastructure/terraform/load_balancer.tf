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

# URL Map with custom domain hostname routing
resource "google_compute_url_map" "cloud_run_url_map" {
  name        = "${var.service_name}-urlmap-${var.environment}"
  description = "URL map for ${var.service_name} - ${var.environment}"

  # If custom domain is configured, redirect all non-matching requests to the canonical domain
  # This prevents access via IP address and ensures strict routing (Opção A: Redirecionamento Canônico)
  # If no custom domain, use default service for direct Cloud Run access
  dynamic "default_url_redirect" {
    for_each = var.custom_domain != "" ? [1] : []
    content {
      https_redirect = true
      host_redirect  = var.custom_domain
      strip_query    = false
    }
  }

  # Only set default_service if custom_domain is NOT configured
  # When custom_domain is set, default_url_redirect takes precedence
  # Note: Terraform requires one of default_service or default_url_redirect, but not both
  # The dynamic block above handles default_url_redirect when custom_domain is set
  # This line handles default_service when custom_domain is NOT set
  # Using try() to safely omit the attribute when custom_domain is set
  default_service = var.custom_domain == "" ? google_compute_backend_service.cloud_run_backend.id : try(google_compute_backend_service.cloud_run_backend.id, null)

  # If custom domain is configured, add hostname rule
  dynamic "host_rule" {
    for_each = var.custom_domain != "" ? [1] : []
    content {
      hosts        = [var.custom_domain]
      path_matcher = "custom-domain"
    }
  }

  dynamic "path_matcher" {
    for_each = var.custom_domain != "" ? [1] : []
    content {
      name            = "custom-domain"
      default_service = google_compute_backend_service.cloud_run_backend.id
    }
  }
}

# HTTP(S) Proxy
resource "google_compute_target_https_proxy" "cloud_run_https_proxy" {
  # Enable HTTPS if SSL is enabled OR custom domain is configured (requires SSL)
  count   = (var.cloud_armor_enable_ssl || var.custom_domain != "") ? 1 : 0
  name    = "${var.service_name}-https-proxy-${var.environment}"
  url_map = google_compute_url_map.cloud_run_url_map.id

  # Use managed SSL certificate if custom domain is configured, otherwise use provided certificate ID
  ssl_certificates = var.custom_domain != "" ? (
    [google_compute_managed_ssl_certificate.domain_cert[0].id]
    ) : (
    var.cloud_armor_ssl_certificate_id != "" ? [var.cloud_armor_ssl_certificate_id] : []
  )

  # Dependencies: URL map always required, SSL certificate if custom domain is configured
  # Note: Terraform will automatically wait for SSL certificate via ssl_certificates reference
  depends_on = [
    google_compute_url_map.cloud_run_url_map
  ]
}

resource "google_compute_target_http_proxy" "cloud_run_http_proxy" {
  # Disable HTTP proxy if SSL is enabled OR custom domain is configured (should use HTTPS)
  count   = (var.cloud_armor_enable_ssl || var.custom_domain != "") ? 0 : 1
  name    = "${var.service_name}-http-proxy-${var.environment}"
  url_map = google_compute_url_map.cloud_run_url_map.id
}

# Global Forwarding Rule (HTTP) - Redirect to HTTPS if custom domain is configured
resource "google_compute_global_forwarding_rule" "cloud_run_http_forwarding" {
  # Disable HTTP forwarding if SSL is enabled OR custom domain is configured
  count      = (var.cloud_armor_enable_ssl || var.custom_domain != "") ? 0 : 1
  name       = "${var.service_name}-http-forwarding-${var.environment}"
  target     = google_compute_target_http_proxy.cloud_run_http_proxy[0].id
  port_range = "80"
  ip_address = google_compute_global_address.cloud_run_ip.address
}

# Global Forwarding Rule (HTTPS)
resource "google_compute_global_forwarding_rule" "cloud_run_https_forwarding" {
  # Enable HTTPS forwarding if SSL is enabled OR custom domain is configured
  count      = (var.cloud_armor_enable_ssl || var.custom_domain != "") ? 1 : 0
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

