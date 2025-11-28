# DEV Environment Configuration
# Copy this file to terraform.tfvars and customize

project_id   = "payments-agent-wpp-dev"
region       = "us-central1"
environment  = "dev"
service_name = "payments-agent"

# Custom Domain Configuration (optional)
# If set, enables HTTPS with managed SSL certificate and blocks direct Cloud Run access
# Leave empty to allow direct Cloud Run URL access
custom_domain = "payments-agent-dev.dscorpsolutions.com" # e.g., "api-dev.example.com"

# Cloud DNS automatic configuration
# If dns_zone_name is set, Terraform will automatically create DNS A record pointing to Load Balancer IP
dns_zone_name = "dscorpsolutions-zone" # Nome da zona DNS criada no bootstrap
# dns_project_id = ""  # Opcional: se zona DNS estiver em outro projeto (deixe vazio se estiver no mesmo projeto)

# Free tier configuration
min_instances = 0
max_instances = 1
cpu           = "1"
memory        = "512Mi"
concurrency   = 80

# Application configuration
session_ttl_minutes = 30
gemini_model        = "gemini-2.5-flash-lite"
log_level           = "INFO"

# Cache TTL configuration
cache_ttl_intent_hours        = 1
cache_ttl_beneficiary_minutes = 30
cache_ttl_validation_hours    = 1

# Cloud Armor Configuration (DEV - More permissive)
cloud_armor_enable                     = true
cloud_armor_rate_limit_requests        = 200 # Higher limit for DEV
cloud_armor_rate_limit_interval        = 60
cloud_armor_enable_adaptive_protection = false # Disable to save costs in DEV
cloud_armor_enable_cdn                 = false

# SSL Configuration
# If custom_domain is set, cloud_armor_enable_ssl will be automatically enabled
# cloud_armor_enable_ssl is only used if custom_domain is empty
cloud_armor_enable_ssl = false
# cloud_armor_ssl_certificate_id = ""  # Only needed if cloud_armor_enable_ssl = true and custom_domain is empty

# Optional: Block/Allow specific IPs
# cloud_armor_blocked_ips = []
# cloud_armor_allowed_ips = []

# Security Configuration
enable_strict_meta_checks = false # Set to false for Demo mode, true for Production
# Note: demo_access_code is now managed via Secret Manager, not as a Terraform variable
# The secret value should be set via GitHub Actions or manually:
# gcloud secrets versions add payments-agent-demo-access-code --data-file=-

# ADK Retry Configuration
# These values should be provided via GitHub Actions as TF_VAR_* environment variables
# Defaults are defined in variables.tf, but should be overridden via CI/CD
# adk_max_retries             = 5
# adk_initial_backoff_seconds = 0.5
# adk_max_backoff_seconds     = 32.0
# adk_backoff_multiplier      = 2.0
# adk_enable_retry            = true
