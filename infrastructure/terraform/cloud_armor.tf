# Cloud Armor Security Policy for DDoS Protection

resource "google_compute_security_policy" "armor_policy" {
  name        = "${var.service_name}-armor-policy-${var.environment}"
  description = "Cloud Armor security policy for ${var.service_name} - ${var.environment} environment"

  # Ensure Compute Engine API is enabled before creating security policy
  depends_on = [google_project_service.compute]

  # Lifecycle: If policy already exists, import it instead of failing
  lifecycle {
    # If you get 409 error, run: terraform import google_compute_security_policy.armor_policy projects/{project_id}/global/securityPolicies/{policy_name}
  }

  # Default rule: Allow all traffic (rate limiting will be applied by higher priority rules)
  rule {
    action   = "allow"
    priority = "2147483647" # Lowest priority (default rule)
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default rule - Allow all traffic (rate limiting applied by higher priority rules)"
  }

  # Note: Cloud Armor doesn't support direct blocking of tor-exit-nodes and anonymous-proxies
  # via expression language. These should be managed via IP lists or external threat intelligence.
  # For now, this rule is commented out. If needed, use Cloud Armor's preconfigured rules
  # or maintain a custom IP list.
  # rule {
  #   action   = "deny(403)"
  #   priority = "900"
  #   match {
  #     versioned_expr = "SRC_IPS_V1"
  #     config {
  #       src_ip_ranges = ["<TOR_IP_LIST>"]  # Maintain manually or via external service
  #     }
  #   }
  #   description = "Block tor-exit-nodes and anonymous-proxies"
  # }

  # Rate limit for /demo/send endpoint (anti-botnet protection)
  rule {
    action   = "rate_based_ban"
    priority = "850"
    match {
      expr {
        expression = "request.path == '/demo/send'"
      }
    }
    rate_limit_options {
      conform_action   = "allow"
      exceed_action    = "deny(429)"
      enforce_on_key   = "IP"
      ban_duration_sec = 60 # Ban for 60 seconds when rate limit is exceeded

      rate_limit_threshold {
        count        = 5
        interval_sec = 60
      }
    }
    description = "Rate limiting for /demo/send endpoint (5 requests per minute per IP)"
  }

  # Toggle: Strict Meta checks (block non-FacebookPlatform User-Agents in production)
  # Only create this rule when enable_strict_meta_checks is true
  dynamic "rule" {
    for_each = var.enable_strict_meta_checks ? [1] : []
    content {
      action   = "deny(403)"
      priority = "800"
      match {
        expr {
          expression = "!request.headers['user-agent'].contains('FacebookPlatform')"
        }
      }
      description = "Block non-FacebookPlatform User-Agents when strict Meta checks are enabled (Production mode)"
    }
  }

  # Rate limiting rule - Protect against DDoS (general)
  rule {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action   = "allow"
      exceed_action    = "deny(429)"
      enforce_on_key   = "IP"
      ban_duration_sec = 60 # Ban for 60 seconds when rate limit is exceeded

      # Rate limiting thresholds (configurable per environment)
      rate_limit_threshold {
        count        = var.cloud_armor_rate_limit_requests
        interval_sec = var.cloud_armor_rate_limit_interval
      }
    }
    description = "Rate limiting protection against DDoS attacks"
  }

  # Optional: Block known bad IPs (if provided)
  dynamic "rule" {
    for_each = length(var.cloud_armor_blocked_ips) > 0 ? [1] : []
    content {
      action   = "deny(403)"
      priority = "100"
      match {
        versioned_expr = "SRC_IPS_V1"
        config {
          src_ip_ranges = var.cloud_armor_blocked_ips
        }
      }
      description = "Block known malicious IPs"
    }
  }

  # Optional: Allow specific IPs (if provided) - Higher priority than rate limit
  dynamic "rule" {
    for_each = length(var.cloud_armor_allowed_ips) > 0 ? [1] : []
    content {
      action   = "allow"
      priority = "50"
      match {
        versioned_expr = "SRC_IPS_V1"
        config {
          src_ip_ranges = var.cloud_armor_allowed_ips
        }
      }
      description = "Allow specific IPs (bypass rate limiting)"
    }
  }

  # Adaptive Protection (if enabled)
  adaptive_protection_config {
    layer_7_ddos_defense_config {
      enable = var.cloud_armor_enable_adaptive_protection
    }
  }
}

