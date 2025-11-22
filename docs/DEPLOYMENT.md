# Deployment Guide - Multi-Project CI/CD Setup

This guide provides step-by-step instructions for setting up the CI/CD pipeline with GitHub Actions and Google Cloud Platform.

## Architecture Overview

- **DEV Project**: `<YOUR_PROJECT_ID>-dev` - Development environment
- **PRD Project**: `<YOUR_PROJECT_ID>` - Production environment
- **Build Strategy**: Build Once - Images built in PRD project, shared with DEV via cross-project IAM
- **Terraform State**: Separate GCS buckets per project for state isolation
- **Cloud Armor**: DDoS protection with rate limiting and adaptive protection (see [CLOUD_ARMOR.md](CLOUD_ARMOR.md))

## Prerequisites

1. **Google Cloud SDK** installed and authenticated
   ```bash
   gcloud --version
   gcloud auth list
   ```

2. **Access to both GCP projects**
   - `<YOUR_PROJECT_ID>-dev` (DEV project)
   - `<YOUR_PROJECT_ID>` (PRD project)

3. **GitHub repository** with Actions enabled

4. **Required permissions** in both GCP projects:
   - Project Owner or Editor
   - Service Account Admin
   - IAM Admin

## Bootstrap Scripts Execution Order

⚠️ **IMPORTANT**: Execute scripts in this exact order. GCS buckets MUST be created first.

### Phase 1: Prerequisites (MUST BE FIRST)

#### 1. Create Terraform State Buckets

```bash
./scripts/bootstrap-terraform-state.sh
```

**What it does:**
- Creates GCS buckets for Terraform state in both projects
- Enables versioning
- Sets uniform bucket-level access

**Output:**
- Bucket names for `backend.conf` files
- Verify buckets exist before proceeding

**Verification:**
```bash
gcloud storage buckets list --project=<YOUR_PROJECT_ID>-dev | grep tf-state
gcloud storage buckets list --project=<YOUR_PROJECT_ID> | grep tf-state
```

### Phase 2: Infrastructure Setup

#### 2. Set up Workload Identity Federation for DEV

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
- Grants necessary IAM roles

**Output:**
- `WIF_PROVIDER_DEV` - Add to GitHub Secrets
- `WIF_SA_DEV` - Add to GitHub Secrets

#### 3. Set up Workload Identity Federation for PRD

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

**Output:**
- `WIF_PROVIDER_PRD` - Add to GitHub Secrets
- `WIF_SA_PRD` - Add to GitHub Secrets

#### 4. Create Artifact Registry

```bash
./scripts/bootstrap-artifact-registry.sh
```

**What it does:**
- Creates Docker repository in PRD project
- Configures repository settings

**Output:**
- Repository name and region
- Add to GitHub Environment Variables

### Phase 3: GitHub Configuration

#### 5. Collect and Format GitHub Values

```bash
./scripts/setup-github-env-vars.sh
```

**What it does:**
- Collects all generated values from bootstrap scripts
- Formats them for GitHub configuration

**Output:**
- Complete list of Environment Variables and Secrets
- Instructions for GitHub configuration

#### 6. Configure GitHub Repository

1. Go to your GitHub repository
2. Navigate to: **Settings > Environments**
3. Create/Edit **dev** environment:
   - Add all `DEV_*` Environment Variables (non-sensitive)
   - Add all DEV Secrets (WIF_PROVIDER_DEV, WIF_SA_DEV, DEV_GOOGLE_API_KEY)
4. Create/Edit **prd** environment:
   - Add all `PRD_*` Environment Variables (non-sensitive)
   - Add all PRD Secrets (WIF_PROVIDER_PRD, WIF_SA_PRD, PRD_GOOGLE_API_KEY)
5. Set shared variables at repository level (optional):
   - `ARTIFACT_REGION`
   - `ARTIFACT_REPO_NAME`

**GitHub Environment Variables (DEV):**
- `DEV_GCP_PROJECT_ID` = `<YOUR_PROJECT_ID>-dev`
- `DEV_GCP_REGION` = `us-central1` (or your preferred region)
- `DEV_GEMINI_MODEL` = `gemini-2.5-flash-lite` (or your preferred model)
- `DEV_LOG_LEVEL` = `INFO`
- `DEV_SESSION_TTL_MINUTES` = `30`
- `DEV_CACHE_TTL_INTENT_HOURS` = `1`
- `DEV_CACHE_TTL_BENEFICIARY_MINUTES` = `30`
- `DEV_CACHE_TTL_VALIDATION_HOURS` = `1`

**GitHub Secrets (DEV):**
- `WIF_PROVIDER_DEV` = (output from `bootstrap-wif-dev.sh` script)
- `WIF_SA_DEV` = (output from `bootstrap-wif-dev.sh` script)
- `DEV_GOOGLE_API_KEY` = (your Google API key for DEV environment)

**GitHub Environment Variables (PRD):**
- `PRD_GCP_PROJECT_ID` = `<YOUR_PROJECT_ID>`
- `PRD_GCP_REGION` = `us-central1` (or your preferred region)
- `PRD_GEMINI_MODEL` = `gemini-2.5-flash` (or your preferred model)
- `PRD_LOG_LEVEL` = `INFO`
- `PRD_SESSION_TTL_MINUTES` = `30`
- `PRD_CACHE_TTL_INTENT_HOURS` = `1`
- `PRD_CACHE_TTL_BENEFICIARY_MINUTES` = `30`
- `PRD_CACHE_TTL_VALIDATION_HOURS` = `1`

**GitHub Secrets (PRD):**
- `WIF_PROVIDER_PRD` = (output from `bootstrap-wif-prd.sh` script)
- `WIF_SA_PRD` = (output from `bootstrap-wif-prd.sh` script)
- `PRD_GOOGLE_API_KEY` = (your Google API key for PRD environment)

### Phase 4: First Terraform Deployment

#### 7. Initial Terraform Deployment

**DEV Deployment:**
```bash
cd infrastructure/terraform
terraform init -backend-config=environments/dev/backend.conf
terraform plan -var-file=environments/dev/terraform.tfvars
terraform apply -var-file=environments/dev/terraform.tfvars
```

**PRD Deployment:**
```bash
terraform init -backend-config=environments/prd/backend.conf
terraform plan -var-file=environments/prd/terraform.tfvars
terraform apply -var-file=environments/prd/terraform.tfvars
```

**Note:** For the first deployment via GitHub Actions, the `image` variable is automatically provided by the workflow. For manual deployment, you'll need to provide it:
```bash
terraform apply -var-file=environments/dev/terraform.tfvars \
  -var="image=<REGION>-docker.pkg.dev/<PRD_PROJECT_ID>/<REPO_NAME>/agent:latest"
```

### Phase 5: Cross-Project IAM Setup

#### 8. Set up Cross-Project IAM

```bash
./scripts/bootstrap-cross-project-iam.sh
```

**What it does:**
- Grants DEV Cloud Run Service Account access to PRD Artifact Registry
- Enables DEV to pull images from PRD

**When to run:** After first `terraform apply` creates the Cloud Run Service Account

**Verification:**
```bash
gcloud artifacts repositories get-iam-policy <REPO_NAME> \
  --location=<REGION> \
  --project=<PRD_PROJECT_ID>
```

## Workflow Triggers

- **DEV**: Automatic deployment on every commit to `develop` branch
- **PRD**: Automatic deployment when a pull request is merged to `main` branch

## Testing the Setup

### Test DEV Deployment

1. Make a test commit to `develop` branch:
   ```bash
   git checkout develop
   git commit --allow-empty -m "test: trigger DEV deployment"
   git push origin develop
   ```

2. Monitor GitHub Actions workflow
3. Verify:
   - Image is built and pushed to Artifact Registry
   - DEV deployment succeeds
   - Service is accessible

### Test PRD Deployment

1. Create a pull request to `main` branch
2. Merge the pull request
3. Monitor GitHub Actions workflow
4. Verify:
   - Image is built and pushed to Artifact Registry
   - PRD deployment succeeds
   - Service is accessible

## Troubleshooting

### Terraform Backend Error

**Problem:** `Error: Failed to get existing workspaces`

**Solution:** Ensure GCS buckets exist before running `terraform init`:
```bash
./scripts/bootstrap-terraform-state.sh
```

### Workload Identity Authentication Error

**Problem:** `Error: failed to get credentials`

**Solution:** Verify WIF configuration:
1. Check GitHub Secrets are set correctly
2. Verify service account has correct IAM roles
3. Check attribute condition matches repository name

### Image Pull Error in DEV

**Problem:** `Error: failed to pull image`

**Solution:** Run cross-project IAM setup:
```bash
./scripts/bootstrap-cross-project-iam.sh
```

### Secret Manager Access Error

**Problem:** `Error: Permission denied on secret`

**Solution:** Verify service account has `roles/secretmanager.admin`:
```bash
gcloud projects get-iam-policy <YOUR_PROJECT_ID>-dev \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-sa@*"
```

## Manual Commands Reference

### Enable Required APIs

```bash
# DEV project
gcloud config set project <YOUR_PROJECT_ID>-dev
gcloud services enable iamcredentials.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable compute.googleapis.com  # For Cloud Armor

# PRD project
gcloud config set project <YOUR_PROJECT_ID>
gcloud services enable iamcredentials.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable compute.googleapis.com  # For Cloud Armor
```

### Verify Setup

```bash
# Check Workload Identity Pools
gcloud iam workload-identity-pools list --location=global --project=<YOUR_PROJECT_ID>-dev
gcloud iam workload-identity-pools list --location=global --project=<YOUR_PROJECT_ID>

# Check Service Accounts
gcloud iam service-accounts list --project=<YOUR_PROJECT_ID>-dev
gcloud iam service-accounts list --project=<YOUR_PROJECT_ID>

# Check Artifact Registry
gcloud artifacts repositories list --project=<YOUR_PROJECT_ID>

# Check Terraform State Buckets
gcloud storage buckets list --project=<YOUR_PROJECT_ID>-dev | grep tf-state
gcloud storage buckets list --project=<YOUR_PROJECT_ID> | grep tf-state
```

## Security Best Practices

1. **Never commit** `.tfvars` files with actual values
2. **Use Workload Identity Federation** (no service account keys)
3. **Rotate secrets** regularly in Secret Manager
4. **Use least-privilege IAM roles** for service accounts
5. **Enable secret versioning** in Secret Manager
6. **Isolate state files** per project (separate GCS buckets)
7. **Limit cross-project access** to read-only for Artifact Registry
8. **Require manual approval** for PRD deployments via GitHub Environments

## Cloud Armor Protection

This deployment includes Cloud Armor for DDoS protection. See [CLOUD_ARMOR.md](CLOUD_ARMOR.md) for detailed information about:
- Rate limiting configuration
- Adaptive Protection
- IP filtering
- Monitoring and troubleshooting

**Important:** Always use the Load Balancer URL (protected by Cloud Armor) in production, not the direct Cloud Run URL.

## Next Steps

After completing the bootstrap process:

1. Verify all GitHub Environment Variables and Secrets are set
2. Test DEV deployment with a test commit to `develop` branch
3. Test PRD deployment with a test PR merge to `main` branch
4. Configure DNS to point to Load Balancer IP (from `terraform output load_balancer_ip`)
5. Monitor deployments and adjust configuration as needed
6. Set up monitoring and alerting for production
7. Review Cloud Armor logs and adjust rate limits based on traffic patterns

