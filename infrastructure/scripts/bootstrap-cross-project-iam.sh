#!/bin/bash
# Bootstrap script to set up cross-project IAM for DEV Cloud Run SA to access PRD Artifact Registry
# This should be run AFTER the first terraform apply creates the Cloud Run Service Account
#
# Usage: ./scripts/bootstrap-cross-project-iam.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project configuration
DEV_PROJECT_ID="payments-agent-wpp-dev"
PRD_PROJECT_ID="payments-agent-wpp"
SERVICE_NAME="payments-agent"

echo -e "${GREEN}=== Bootstrap Cross-Project IAM ===${NC}"
echo "Granting DEV Cloud Run SA access to PRD Artifact Registry"
echo ""

# Get DEV Cloud Run Service Account
echo -e "${YELLOW}Retrieving DEV Cloud Run Service Account...${NC}"
gcloud config set project "${DEV_PROJECT_ID}"

# Try to get the service account from Cloud Run service
CLOUD_RUN_SA=$(gcloud run services describe "${SERVICE_NAME}" \
    --region="us-central1" \
    --project="${DEV_PROJECT_ID}" \
    --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || echo "")

if [ -z "$CLOUD_RUN_SA" ]; then
    # If service doesn't exist yet, construct the expected SA name
    CLOUD_RUN_SA="${SERVICE_NAME}-sa@${DEV_PROJECT_ID}.iam.gserviceaccount.com"
    echo -e "${YELLOW}Cloud Run service not found, using expected SA: ${CLOUD_RUN_SA}${NC}"
    echo -e "${YELLOW}Note: This script should be run after terraform apply creates the service${NC}"
else
    echo -e "${GREEN}Found Cloud Run Service Account: ${CLOUD_RUN_SA}${NC}"
fi
echo ""

# Get Artifact Registry repository name
echo -e "${YELLOW}Retrieving Artifact Registry repository...${NC}"
gcloud config set project "${PRD_PROJECT_ID}"

REPO_NAME=$(gcloud artifacts repositories list \
    --location="us-central1" \
    --project="${PRD_PROJECT_ID}" \
    --format="value(name)" \
    --filter="format:DOCKER" \
    --limit=1)

if [ -z "$REPO_NAME" ]; then
    echo -e "${RED}Error: No Artifact Registry repository found in PRD project${NC}"
    echo "Please run bootstrap-artifact-registry.sh first"
    exit 1
fi

REPO_ID=$(basename "$REPO_NAME")
echo -e "${GREEN}Found repository: ${REPO_ID}${NC}"
echo ""

# Grant Artifact Registry Reader role to DEV Cloud Run SA in PRD project
echo -e "${YELLOW}Granting Artifact Registry Reader role...${NC}"
gcloud artifacts repositories add-iam-policy-binding "${REPO_ID}" \
    --location="us-central1" \
    --project="${PRD_PROJECT_ID}" \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/artifactregistry.reader"

echo -e "${GREEN}✓ IAM binding added${NC}"
echo ""

echo -e "${GREEN}=== Bootstrap Complete ===${NC}"
echo ""
echo -e "${GREEN}Cross-project IAM configured:${NC}"
echo "Service Account: ${CLOUD_RUN_SA}"
echo "Repository: ${REPO_ID}"
echo "Role: roles/artifactregistry.reader"
echo ""
echo -e "${GREEN}DEV Cloud Run can now pull images from PRD Artifact Registry${NC}"
echo ""

