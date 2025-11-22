# DEV Environment Configuration
# This file contains static configuration values
# Dynamic values (like image) are passed via TF_VAR_* environment variables in the workflow

project_id = "payments-agent-wpp-dev"
region     = "us-central1"
environment = "dev"
service_name = "payments-agent"

# Image will be provided by GitHub Actions workflow via TF_VAR_image
# image is passed via environment variable, not here

# Free tier configuration
min_instances = 0
max_instances = 10
cpu          = "1"
memory       = "512Mi"
concurrency  = 80

# Application configuration
# These can be overridden via TF_VAR_* environment variables in workflow
session_ttl_minutes = 30
gemini_model = "gemini-2.5-flash-lite"
log_level = "INFO"

# Cache TTL configuration
# These can be overridden via TF_VAR_* environment variables in workflow
cache_ttl_intent_hours = 1
cache_ttl_beneficiary_minutes = 30
cache_ttl_validation_hours = 1

# Cloud Armor Configuration (DEV - More permissive)
cloud_armor_enable = true
cloud_armor_rate_limit_requests = 200  # Higher limit for DEV
cloud_armor_rate_limit_interval = 60
cloud_armor_enable_adaptive_protection = false  # Disable to save costs in DEV
cloud_armor_enable_cdn = false
cloud_armor_enable_ssl = false
# cloud_armor_blocked_ips = []  # Optional: Block specific IPs
# cloud_armor_allowed_ips = []   # Optional: Allow specific IPs (bypass rate limit)

