# Basic monitoring setup (free tier)
# Cloud Logging is enabled by default for Cloud Run
# Cloud Monitoring basic metrics are free

# Optional: Create alert policy for errors (if needed)
# This is commented out as it may require paid tier for some features

# resource "google_monitoring_alert_policy" "error_rate" {
#   display_name = "High Error Rate - ${var.service_name}"
#   combiner     = "OR"
#
#   conditions {
#     display_name = "Error rate too high"
#     condition_threshold {
#       filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.service_name}\""
#       duration        = "300s"
#       comparison      = "COMPARISON_GT"
#       threshold_value = 0.05
#
#       aggregations {
#         alignment_period   = "60s"
#         per_series_aligner = "ALIGN_RATE"
#       }
#     }
#   }
# }

