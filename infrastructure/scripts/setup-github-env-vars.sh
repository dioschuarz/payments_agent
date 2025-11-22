#!/bin/bash
# Helper script to collect and format all values for GitHub Environment Variables and Secrets
# This script reads outputs from bootstrap scripts and formats them for GitHub configuration
#
# Usage: ./scripts/setup-github-env-vars.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== GitHub Environment Variables and Secrets Configuration ===${NC}"
echo ""
echo -e "${YELLOW}This script helps you collect all values needed for GitHub configuration.${NC}"
echo -e "${YELLOW}Run this after executing all bootstrap scripts.${NC}"
echo ""

# Project IDs
DEV_PROJECT_ID="payments-agent-wpp-dev"
PRD_PROJECT_ID="payments-agent-wpp"

# Get WIF Provider for DEV
echo -e "${BLUE}Collecting DEV Workload Identity Federation values...${NC}"
gcloud config set project "${DEV_PROJECT_ID}" &>/dev/null
DEV_POOL_NAME=$(gcloud iam workload-identity-pools describe "github-actions-pool" \
    --location="global" \
    --project="${DEV_PROJECT_ID}" \
    --format="value(name)" 2>/dev/null || echo "")

if [ -n "$DEV_POOL_NAME" ]; then
    DEV_PROVIDER_NAME=$(gcloud iam workload-identity-pools providers describe "github-provider" \
        --location="global" \
        --workload-identity-pool="github-actions-pool" \
        --project="${DEV_PROJECT_ID}" \
        --format="value(name)" 2>/dev/null || echo "")
    DEV_SA="${DEV_PROJECT_ID}@${DEV_PROJECT_ID}.iam.gserviceaccount.com"
    DEV_SA=$(echo "$DEV_SA" | sed "s/@${DEV_PROJECT_ID}/-sa@${DEV_PROJECT_ID}/")
    DEV_SA="github-actions-sa@${DEV_PROJECT_ID}.iam.gserviceaccount.com"
else
    DEV_PROVIDER_NAME="<Run bootstrap-wif-dev.sh first>"
    DEV_SA="<Run bootstrap-wif-dev.sh first>"
fi

# Get WIF Provider for PRD
echo -e "${BLUE}Collecting PRD Workload Identity Federation values...${NC}"
gcloud config set project "${PRD_PROJECT_ID}" &>/dev/null
PRD_POOL_NAME=$(gcloud iam workload-identity-pools describe "github-actions-pool" \
    --location="global" \
    --project="${PRD_PROJECT_ID}" \
    --format="value(name)" 2>/dev/null || echo "")

if [ -n "$PRD_POOL_NAME" ]; then
    PRD_PROVIDER_NAME=$(gcloud iam workload-identity-pools providers describe "github-provider" \
        --location="global" \
        --workload-identity-pool="github-actions-pool" \
        --project="${PRD_PROJECT_ID}" \
        --format="value(name)" 2>/dev/null || echo "")
    PRD_SA="github-actions-sa@${PRD_PROJECT_ID}.iam.gserviceaccount.com"
else
    PRD_PROVIDER_NAME="<Run bootstrap-wif-prd.sh first>"
    PRD_SA="<Run bootstrap-wif-prd.sh first>"
fi

# Get Artifact Registry info
echo -e "${BLUE}Collecting Artifact Registry values...${NC}"
ARTIFACT_REGION="us-central1"
ARTIFACT_REPO_NAME=$(gcloud artifacts repositories list \
    --location="${ARTIFACT_REGION}" \
    --project="${PRD_PROJECT_ID}" \
    --format="value(name)" \
    --filter="format:DOCKER" \
    --limit=1 2>/dev/null | xargs basename 2>/dev/null || echo "docker-repo")

echo ""
echo -e "${GREEN}=== GitHub Configuration Values ===${NC}"
echo ""

# DEV Environment
echo -e "${YELLOW}--- DEV Environment (Repository Settings > Environments > dev) ---${NC}"
echo ""
echo -e "${GREEN}Environment Variables (non-sensitive):${NC}"
echo "DEV_GCP_PROJECT_ID=${DEV_PROJECT_ID}"
echo "DEV_GCP_REGION=us-central1"
echo "DEV_GEMINI_MODEL=gemini-2.5-flash-lite"
echo "DEV_LOG_LEVEL=INFO"
echo "DEV_SESSION_TTL_MINUTES=30"
echo "DEV_CACHE_TTL_INTENT_HOURS=1"
echo "DEV_CACHE_TTL_BENEFICIARY_MINUTES=30"
echo "DEV_CACHE_TTL_VALIDATION_HOURS=1"
echo ""
echo -e "${GREEN}Secrets (sensitive):${NC}"
echo "WIF_PROVIDER_DEV=${DEV_PROVIDER_NAME}"
echo "WIF_SA_DEV=${DEV_SA}"
echo "DEV_GOOGLE_API_KEY=<Your Google API Key for DEV>"
echo ""

# PRD Environment
echo -e "${YELLOW}--- PRD Environment (Repository Settings > Environments > prd) ---${NC}"
echo ""
echo -e "${GREEN}Environment Variables (non-sensitive):${NC}"
echo "PRD_GCP_PROJECT_ID=${PRD_PROJECT_ID}"
echo "PRD_GCP_REGION=us-central1"
echo "PRD_GEMINI_MODEL=gemini-2.5-flash"
echo "PRD_LOG_LEVEL=INFO"
echo "PRD_SESSION_TTL_MINUTES=30"
echo "PRD_CACHE_TTL_INTENT_HOURS=1"
echo "PRD_CACHE_TTL_BENEFICIARY_MINUTES=30"
echo "PRD_CACHE_TTL_VALIDATION_HOURS=1"
echo ""
echo -e "${GREEN}Secrets (sensitive):${NC}"
echo "WIF_PROVIDER_PRD=${PRD_PROVIDER_NAME}"
echo "WIF_SA_PRD=${PRD_SA}"
echo "PRD_GOOGLE_API_KEY=<Your Google API Key for PRD>"
echo ""

# Shared Environment Variables
echo -e "${YELLOW}--- Shared Environment Variables (can be set at repository level) ---${NC}"
echo ""
echo "ARTIFACT_REGION=${ARTIFACT_REGION}"
echo "ARTIFACT_REPO_NAME=${ARTIFACT_REPO_NAME}"
echo ""

echo -e "${GREEN}=== Configuration Instructions ===${NC}"
echo ""
echo "1. Go to your GitHub repository"
echo "2. Navigate to: Settings > Environments"
echo "3. Create/Edit 'dev' environment:"
echo "   - Add all DEV_* Environment Variables"
echo "   - Add all DEV Secrets (WIF_PROVIDER_DEV, WIF_SA_DEV, DEV_GOOGLE_API_KEY)"
echo "4. Create/Edit 'prd' environment:"
echo "   - Add all PRD_* Environment Variables"
echo "   - Add all PRD Secrets (WIF_PROVIDER_PRD, WIF_SA_PRD, PRD_GOOGLE_API_KEY)"
echo "5. Set shared variables at repository level (optional):"
echo "   - ARTIFACT_REGION"
echo "   - ARTIFACT_REPO_NAME"
echo ""

