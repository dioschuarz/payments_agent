variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "payments-agent"
}

variable "image" {
  description = "Container image URL"
  type        = string
}

variable "min_instances" {
  description = "Minimum number of instances (0 for free tier)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "cpu" {
  description = "CPU allocation (1 = 1 vCPU, free tier allows up to 2)"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocation (512Mi for free tier)"
  type        = string
  default     = "512Mi"
}

variable "concurrency" {
  description = "Number of concurrent requests per instance"
  type        = number
  default     = 80
}

variable "session_ttl_minutes" {
  description = "Session TTL in minutes"
  type        = number
  default     = 30
}

variable "gemini_model" {
  description = "Gemini model name to use (e.g., gemini-2.5-flash-lite, gemini-2.5-flash, gemini-1.5-pro)"
  type        = string
  default     = "gemini-2.5-flash-lite"
}

variable "environment" {
  description = "Environment name (dev, prd)"
  type        = string
}

variable "log_level" {
  description = "Logging level (INFO, DEBUG, ERROR)"
  type        = string
  default     = "INFO"
}

variable "cache_ttl_intent_hours" {
  description = "Intent cache TTL in hours"
  type        = number
  default     = 1
}

variable "cache_ttl_beneficiary_minutes" {
  description = "Beneficiary cache TTL in minutes"
  type        = number
  default     = 30
}

variable "cache_ttl_validation_hours" {
  description = "Validation cache TTL in hours"
  type        = number
  default     = 1
}

# Cloud Armor Configuration
variable "cloud_armor_enable" {
  description = "Enable Cloud Armor protection"
  type        = bool
  default     = true
}

variable "cloud_armor_rate_limit_requests" {
  description = "Maximum requests per interval for rate limiting"
  type        = number
  default     = 100
}

variable "cloud_armor_rate_limit_interval" {
  description = "Rate limiting interval in seconds"
  type        = number
  default     = 60
}

variable "cloud_armor_blocked_ips" {
  description = "List of IP addresses/CIDR blocks to block"
  type        = list(string)
  default     = []
}

variable "cloud_armor_allowed_ips" {
  description = "List of IP addresses/CIDR blocks to allow (bypass rate limiting)"
  type        = list(string)
  default     = []
}

variable "cloud_armor_enable_adaptive_protection" {
  description = "Enable Cloud Armor Adaptive Protection (Layer 7 DDoS defense)"
  type        = bool
  default     = false # Enable for PRD, disable for DEV to save costs
}

variable "cloud_armor_enable_cdn" {
  description = "Enable CDN for backend service"
  type        = bool
  default     = false
}

variable "cloud_armor_enable_ssl" {
  description = "Enable HTTPS/SSL for load balancer"
  type        = bool
  default     = false # Set to true if you have SSL certificate
}

variable "cloud_armor_ssl_certificate_id" {
  description = "SSL certificate ID for HTTPS (if cloud_armor_enable_ssl is true and custom_domain is not set)"
  type        = string
  default     = ""
}

variable "custom_domain" {
  description = "Custom domain name for the service (e.g., api.example.com). If set, enables HTTPS with managed SSL certificate and blocks direct Cloud Run access."
  type        = string
  default     = ""
}

variable "dns_zone_name" {
  description = "Cloud DNS zone name where the custom domain will be configured (e.g., 'dscorpsolutions-zone'). Leave empty if DNS is managed externally. If set, Terraform will automatically create DNS record A pointing to Load Balancer IP."
  type        = string
  default     = ""
}

variable "dns_project_id" {
  description = "GCP Project ID where DNS zone is located (if different from project_id). Defaults to project_id. Useful if DNS zone is in a shared project."
  type        = string
  default     = ""
}

