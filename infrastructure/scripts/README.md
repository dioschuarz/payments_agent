# Bootstrap Scripts

This directory contains bootstrap scripts for setting up the CI/CD infrastructure.

## Scripts Overview

### 1. bootstrap-terraform-state.sh

Creates GCS buckets for Terraform state files in both DEV and PRD projects.

**Usage:**
```bash
./scripts/bootstrap-terraform-state.sh
```

**What it does:**
- Creates `<PROJECT_ID>-dev-tf-state` bucket in DEV project
- Creates `<PROJECT_ID>-tf-state` bucket in PRD project
- Enables versioning on both buckets
- Sets uniform bucket-level access

**⚠️ IMPORTANT:** This MUST be run FIRST before any `terraform init` command.

---

### 2. bootstrap-wif-dev.sh

Sets up Workload Identity Federation for DEV project.

**Usage:**
```bash
./scripts/bootstrap-wif-dev.sh <GITHUB_OWNER> <GITHUB_REPO>
```

**Example:**
```bash
./scripts/bootstrap-wif-dev.sh myorg payments_agent
```

**What it does:**
- Creates Workload Identity Pool
- Creates GitHub OIDC provider
- Creates Service Account for GitHub Actions
- Grants necessary IAM roles (Cloud Run Admin, Secret Manager Admin, Service Account User)

**Output:** Provides `WIF_PROVIDER_DEV` and `WIF_SA_DEV` values for GitHub Secrets.

---

### 3. bootstrap-wif-prd.sh

Sets up Workload Identity Federation for PRD project.

**Usage:**
```bash
./scripts/bootstrap-wif-prd.sh <GITHUB_OWNER> <GITHUB_REPO>
```

**Example:**
```bash
./scripts/bootstrap-wif-prd.sh myorg payments_agent
```

**What it does:**
- Same as DEV, but for PRD project
- Includes Artifact Registry Writer role

**Output:** Provides `WIF_PROVIDER_PRD` and `WIF_SA_PRD` values for GitHub Secrets.

---

### 4. bootstrap-artifact-registry.sh

Creates Artifact Registry repository in PRD project.

**Usage:**
```bash
./scripts/bootstrap-artifact-registry.sh
```

**What it does:**
- Creates Docker repository in PRD project
- Configures repository settings
- Enables Artifact Registry API

**Output:** Provides repository name and region for GitHub Environment Variables.

---

### 5. bootstrap-dns-zone.sh

Creates DNS zone in Cloud DNS (DEV project) for custom domain management.

**Usage:**
```bash
./scripts/bootstrap-dns-zone.sh
```

**What it does:**
- Creates DNS zone `dscorpsolutions-zone` for `dscorpsolutions.com` domain
- Enables Cloud DNS API in DEV project
- Grants `roles/dns.admin` to GitHub Actions service account
- Displays nameservers for domain registrar configuration

**⚠️ IMPORTANT:** 
- This creates the DNS zone once (shared by all agents)
- Individual DNS A records are created automatically by Terraform per agent
- After running, configure nameservers in your domain registrar (Google Domains)

**Output:** 
- DNS zone created in Cloud DNS
- Nameservers displayed (for manual configuration in domain registrar)
- Permissions configured for GitHub Actions service account

---

### 6. bootstrap-cross-project-iam.sh

Sets up cross-project IAM for DEV Cloud Run SA to access PRD Artifact Registry.

**Usage:**
```bash
./scripts/bootstrap-cross-project-iam.sh
```

**What it does:**
- Retrieves DEV Cloud Run Service Account
- Grants `roles/artifactregistry.reader` role in PRD project
- Enables DEV to pull images from PRD Artifact Registry

**⚠️ IMPORTANT:** Run this AFTER the first `terraform apply` creates the Cloud Run Service Account.

---

### 6. setup-github-env-vars.sh

Helper script to collect and format all values for GitHub configuration.

**Usage:**
```bash
./scripts/setup-github-env-vars.sh
```

**What it does:**
- Collects all generated values from bootstrap scripts
- Formats them for GitHub Environment Variables and Secrets
- Provides instructions for GitHub configuration

**Output:** Complete list of Environment Variables and Secrets with instructions.

---

## Execution Order

Execute scripts in this exact order:

1. `bootstrap-terraform-state.sh` ⚠️ MUST BE FIRST
2. `bootstrap-wif-dev.sh`
3. `bootstrap-wif-prd.sh`
4. `bootstrap-artifact-registry.sh`
5. `setup-github-env-vars.sh`
6. Configure GitHub (manual step)
7. First Terraform apply (or deploy via GitHub Actions)
8. `bootstrap-dns-zone.sh` (optional - only if using custom domain)
   - **Note:** In GitHub Actions, this runs automatically in `deploy-dev` job after APIs are enabled
   - If running manually, execute after first terraform apply
9. Configure nameservers in domain registrar (if DNS zone was created)
10. `bootstrap-cross-project-iam.sh`

## Prerequisites

- Google Cloud SDK installed and authenticated
- Access to both GCP projects (`<YOUR_PROJECT_ID>-dev` and `<YOUR_PROJECT_ID>`)
- Required permissions (Project Owner/Editor, Service Account Admin, IAM Admin)

## Troubleshooting

### Script fails with "permission denied"

Ensure you have the required permissions in both GCP projects:
- Project Owner or Editor
- Service Account Admin
- IAM Admin

### Script fails with "API not enabled"

Enable required APIs:
```bash
gcloud services enable iamcredentials.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable run.googleapis.com
```

### Terraform init fails after bootstrap

Verify buckets were created:
```bash
gcloud storage buckets list --project=<YOUR_PROJECT_ID>-dev | grep tf-state
gcloud storage buckets list --project=<YOUR_PROJECT_ID> | grep tf-state
```

## See Also

- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) - Complete deployment guide
- [README.md](../README.md) - Project overview

