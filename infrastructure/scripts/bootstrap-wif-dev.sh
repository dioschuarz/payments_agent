#!/bin/bash
# Bootstrap script to set up Workload Identity Federation for DEV project
#
# Usage: ./scripts/bootstrap-wif-dev.sh [GITHUB_OWNER] [GITHUB_REPO]
#
# Example: ./scripts/bootstrap-wif-dev.sh myorg payments_agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="payments-agent-wpp-dev"
POOL_ID="github-actions-pool"
PROVIDER_ID="github-provider"
SERVICE_ACCOUNT_ID="github-actions-sa"
SERVICE_ACCOUNT_NAME="GitHub Actions Service Account"

# GitHub configuration
GITHUB_OWNER=${1:-"YOUR_GITHUB_OWNER"}
GITHUB_REPO=${2:-"YOUR_GITHUB_REPO"}

if [ "$GITHUB_OWNER" == "YOUR_GITHUB_OWNER" ] || [ "$GITHUB_REPO" == "YOUR_GITHUB_REPO" ]; then
    echo -e "${RED}Error: Please provide GitHub owner and repository${NC}"
    echo "Usage: $0 <github_owner> <github_repo>"
    echo "Example: $0 myorg payments_agent"
    exit 1
fi

echo -e "${GREEN}=== Bootstrap Workload Identity Federation for DEV ===${NC}"
echo "Project: ${PROJECT_ID}"
echo "GitHub: ${GITHUB_OWNER}/${GITHUB_REPO}"
echo ""

# Set project
gcloud config set project "${PROJECT_ID}"

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable iamcredentials.googleapis.com --project="${PROJECT_ID}"
gcloud services enable iam.googleapis.com --project="${PROJECT_ID}"
gcloud services enable secretmanager.googleapis.com --project="${PROJECT_ID}"
gcloud services enable run.googleapis.com --project="${PROJECT_ID}"
gcloud services enable cloudresourcemanager.googleapis.com --project="${PROJECT_ID}"
echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Create Workload Identity Pool
echo -e "${YELLOW}Creating Workload Identity Pool...${NC}"
if gcloud iam workload-identity-pools describe "${POOL_ID}" \
    --location="global" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Pool ${POOL_ID} already exists, skipping creation${NC}"
else
    gcloud iam workload-identity-pools create "${POOL_ID}" \
        --location="global" \
        --project="${PROJECT_ID}" \
        --display-name="GitHub Actions Pool"
    echo -e "${GREEN}✓ Pool created${NC}"
fi
echo ""

# Create OIDC Provider
echo -e "${YELLOW}Creating OIDC Provider...${NC}"
if gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Provider ${PROVIDER_ID} already exists, skipping creation${NC}"
else
    gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
        --location="global" \
        --workload-identity-pool="${POOL_ID}" \
        --project="${PROJECT_ID}" \
        --display-name="GitHub Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --attribute-condition="assertion.repository == '${GITHUB_OWNER}/${GITHUB_REPO}'" \
        --issuer-uri="https://token.actions.githubusercontent.com"
    echo -e "${GREEN}✓ Provider created${NC}"
fi
echo ""

# Get pool name
POOL_NAME=$(gcloud iam workload-identity-pools describe "${POOL_ID}" \
    --location="global" \
    --project="${PROJECT_ID}" \
    --format="value(name)")

# Create Service Account
echo -e "${YELLOW}Creating Service Account...${NC}"
if gcloud iam service-accounts describe "${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Service Account ${SERVICE_ACCOUNT_ID} already exists, skipping creation${NC}"
else
    gcloud iam service-accounts create "${SERVICE_ACCOUNT_ID}" \
        --project="${PROJECT_ID}" \
        --display-name="${SERVICE_ACCOUNT_NAME}"
    echo -e "${GREEN}✓ Service Account created${NC}"
fi
echo ""

# Allow GitHub to impersonate the service account
echo -e "${YELLOW}Granting Workload Identity User role...${NC}"
gcloud iam service-accounts add-iam-policy-binding \
    "${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/${GITHUB_OWNER}/${GITHUB_REPO}"
echo -e "${GREEN}✓ IAM binding added${NC}"
echo ""

# Grant necessary roles to service account
echo -e "${YELLOW}Granting IAM roles to service account...${NC}"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

echo -e "${GREEN}✓ IAM roles granted${NC}"
echo ""

# Grant Storage permissions for Terraform state bucket
echo -e "${YELLOW}Granting Storage permissions for Terraform state bucket...${NC}"
DEV_BUCKET="payments-agent-wpp-dev-tf-state"
PRD_BUCKET="payments-agent-wpp-tf-state"

if [ "${PROJECT_ID}" == "payments-agent-wpp-dev" ]; then
    BUCKET_NAME="${DEV_BUCKET}"
elif [ "${PROJECT_ID}" == "payments-agent-wpp" ]; then
    BUCKET_NAME="${PRD_BUCKET}"
else
    BUCKET_NAME=""
fi

if [ -n "${BUCKET_NAME}" ]; then
    # Check if bucket exists before granting permissions
    if gcloud storage buckets describe "gs://${BUCKET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
        gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectAdmin "gs://${BUCKET_NAME}"
        echo -e "${GREEN}✓ Storage permissions granted on bucket ${BUCKET_NAME}${NC}"
    else
        echo -e "${YELLOW}⚠ Bucket ${BUCKET_NAME} does not exist yet. Run bootstrap-terraform-state.sh first.${NC}"
        echo -e "${YELLOW}  Then run fix-terraform-state-permissions.sh to grant permissions.${NC}"
    fi
fi
echo ""

# Get provider name
PROVIDER_NAME=$(gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --project="${PROJECT_ID}" \
    --format="value(name)")

echo -e "${GREEN}=== Bootstrap Complete ===${NC}"
echo ""
echo -e "${GREEN}GitHub Secrets/Environment Variables for DEV:${NC}"
echo "WIF_PROVIDER_DEV=${PROVIDER_NAME}"
echo "WIF_SA_DEV=${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
echo ""
echo -e "${YELLOW}Add these to GitHub:${NC}"
echo "1. Go to Repository Settings > Environments > dev"
echo "2. Add Secret: WIF_PROVIDER_DEV = ${PROVIDER_NAME}"
echo "3. Add Secret: WIF_SA_DEV = ${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
echo ""

