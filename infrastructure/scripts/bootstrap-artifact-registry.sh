#!/bin/bash
# Bootstrap script to create Artifact Registry repository in PRD project
#
# Usage: ./scripts/bootstrap-artifact-registry.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="payments-agent-wpp"
REPO_NAME="docker-repo"
REGION="us-central1"
DESCRIPTION="Docker repository for payments-agent images"

echo -e "${GREEN}=== Bootstrap Artifact Registry ===${NC}"
echo "Project: ${PROJECT_ID}"
echo "Repository: ${REPO_NAME}"
echo "Region: ${REGION}"
echo ""

# Set project
gcloud config set project "${PROJECT_ID}"

# Enable required API
echo -e "${YELLOW}Enabling Artifact Registry API...${NC}"
gcloud services enable artifactregistry.googleapis.com --project="${PROJECT_ID}"
echo -e "${GREEN}✓ API enabled${NC}"
echo ""

# Create repository
echo -e "${YELLOW}Creating Artifact Registry repository...${NC}"
if gcloud artifacts repositories describe "${REPO_NAME}" \
    --location="${REGION}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Repository ${REPO_NAME} already exists, skipping creation${NC}"
else
    gcloud artifacts repositories create "${REPO_NAME}" \
        --repository-format=docker \
        --location="${REGION}" \
        --project="${PROJECT_ID}" \
        --description="${DESCRIPTION}"
    echo -e "${GREEN}✓ Repository created${NC}"
fi
echo ""

# Get repository URL
REPO_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"

echo -e "${GREEN}=== Bootstrap Complete ===${NC}"
echo ""
echo -e "${GREEN}Artifact Registry Configuration:${NC}"
echo "Repository URL: ${REPO_URL}"
echo "Repository Name: ${REPO_NAME}"
echo "Region: ${REGION}"
echo ""
echo -e "${YELLOW}GitHub Environment Variables:${NC}"
echo "ARTIFACT_REGION=${REGION}"
echo "ARTIFACT_REPO_NAME=${REPO_NAME}"
echo ""
echo -e "${YELLOW}Add these to GitHub:${NC}"
echo "1. Go to Repository Settings > Environments > dev (or prd)"
echo "2. Add Environment Variable: ARTIFACT_REGION = ${REGION}"
echo "3. Add Environment Variable: ARTIFACT_REPO_NAME = ${REPO_NAME}"
echo ""

