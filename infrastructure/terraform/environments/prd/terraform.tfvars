# PRD Environment Configuration
# This file contains static configuration values
# Dynamic values (like image) are passed via TF_VAR_* environment variables in the workflow

project_id   = "payments-agent-wpp"
region       = "us-central1"
environment  = "prd"
service_name = "payments-agent"

# Image will be provided by GitHub Actions workflow via TF_VAR_image
# image is passed via environment variable, not here

# Production configuration
min_instances = 1
max_instances = 10
cpu           = "1"
memory        = "512Mi"
concurrency   = 80

# Application configuration
# These can be overridden via TF_VAR_* environment variables in workflow
session_ttl_minutes = 30
gemini_model        = "gemini-2.5-flash"
log_level           = "INFO"

# Cache TTL configuration
# These can be overridden via TF_VAR_* environment variables in workflow
cache_ttl_intent_hours        = 1
cache_ttl_beneficiary_minutes = 30
cache_ttl_validation_hours    = 1

# Cloud Armor Configuration (PRD - Strict protection)
cloud_armor_enable                     = true
cloud_armor_rate_limit_requests        = 100 # Stricter limit for PRD
cloud_armor_rate_limit_interval        = 60
cloud_armor_enable_adaptive_protection = true  # Enable Layer 7 DDoS protection for PRD
cloud_armor_enable_cdn                 = false # Enable if you want CDN caching
cloud_armor_enable_ssl                 = false # Set to true and provide certificate ID if you have SSL
# cloud_armor_ssl_certificate_id = ""  # SSL certificate ID if using HTTPS
# cloud_armor_blocked_ips = []  # Optional: Block known malicious IPs
# cloud_armor_allowed_ips = []   # Optional: Allow specific IPs (bypass rate limit)

