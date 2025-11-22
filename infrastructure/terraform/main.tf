terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Backend configuration is provided via -backend-config flag
  # Example: terraform init -backend-config=environments/dev/backend.conf
  backend "gcs" {
    # bucket and prefix are set via backend-config file
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

