# Custom Domain Configuration for Cloud Run via Load Balancer
# This allows access only through custom domain, blocking direct Cloud Run URL access

# Managed SSL Certificate (Google-managed SSL certificate)
resource "google_compute_managed_ssl_certificate" "domain_cert" {
  count = var.custom_domain != "" ? 1 : 0
  name  = "${var.service_name}-ssl-cert-${var.environment}"

  managed {
    domains = [var.custom_domain]
  }

  # SSL certificate takes time to provision (can take up to 60 minutes)
  # We'll use lifecycle to prevent recreation issues
  lifecycle {
    create_before_destroy = true
    # Ignore changes to domain if it's being provisioned
    ignore_changes = [managed[0].domains]
  }

  # Ensure Compute Engine API is enabled before creating SSL certificate
  depends_on = [google_project_service.compute]
}

# Data source to read DNS zone (created via bootstrap)
data "google_dns_managed_zone" "domain_zone" {
  count   = var.custom_domain != "" && var.dns_zone_name != "" ? 1 : 0
  name    = var.dns_zone_name
  project = var.dns_project_id != "" ? var.dns_project_id : var.project_id

  depends_on = [google_project_service.dns]
}

# Automatic DNS Record A - Points custom domain to Load Balancer IP
# This record is created/updated automatically by Terraform
resource "google_dns_record_set" "custom_domain_a" {
  count        = var.custom_domain != "" && var.dns_zone_name != "" ? 1 : 0
  name         = "${var.custom_domain}."
  type         = "A"
  ttl          = 300
  managed_zone = data.google_dns_managed_zone.domain_zone[0].name
  project      = var.dns_project_id != "" ? var.dns_project_id : var.project_id
  rrdatas      = [google_compute_global_address.cloud_run_ip.address]

  depends_on = [
    google_compute_global_address.cloud_run_ip,
    google_project_service.dns,
    data.google_dns_managed_zone.domain_zone
  ]
}

# Domain mapping (alternative approach - not used if using Load Balancer)
# We're using Load Balancer approach, but keeping this commented for reference
# resource "google_cloud_run_domain_mapping" "domain" {
#   count    = var.custom_domain != "" ? 1 : 0
#   name     = var.custom_domain
#   location = var.region
# 
#   metadata {
#     namespace = var.project_id
#   }
# 
#   spec {
#     route_name = google_cloud_run_v2_service.service.name
#   }
# }

