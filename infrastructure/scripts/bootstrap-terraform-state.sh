#!/bin/bash
# Bootstrap script to create GCS buckets for Terraform state files
# This MUST be run FIRST before any terraform init command
#
# Usage: ./scripts/bootstrap-terraform-state.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project IDs
DEV_PROJECT_ID="payments-agent-wpp-dev"
PRD_PROJECT_ID="payments-agent-wpp"

# Bucket names
DEV_BUCKET="payments-agent-wpp-dev-tf-state"
PRD_BUCKET="payments-agent-wpp-tf-state"

# Region
REGION="us-central1"

echo -e "${GREEN}=== Bootstrap Terraform State Buckets ===${NC}"
echo ""

# Function to create bucket
create_bucket() {
    local project_id=$1
    local bucket_name=$2
    local location=$3
    
    echo -e "${YELLOW}Creating bucket ${bucket_name} in project ${project_id}...${NC}"
    
    # Check if bucket already exists
    if gcloud storage buckets describe "gs://${bucket_name}" --project="${project_id}" &>/dev/null; then
        echo -e "${YELLOW}Bucket ${bucket_name} already exists, skipping creation${NC}"
    else
        # Create bucket
        gcloud storage buckets create "gs://${bucket_name}" \
            --project="${project_id}" \
            --location="${location}" \
            --uniform-bucket-level-access
        
        echo -e "${GREEN}✓ Bucket ${bucket_name} created${NC}"
    fi
    
    # Enable versioning
    echo -e "${YELLOW}Enabling versioning on ${bucket_name}...${NC}"
    gcloud storage buckets update "gs://${bucket_name}" \
        --project="${project_id}" \
        --versioning
    
    echo -e "${GREEN}✓ Versioning enabled on ${bucket_name}${NC}"
    echo ""
}

# Create DEV bucket
echo -e "${GREEN}--- DEV Project Bucket ---${NC}"
gcloud config set project "${DEV_PROJECT_ID}"
create_bucket "${DEV_PROJECT_ID}" "${DEV_BUCKET}" "${REGION}"

# Create PRD bucket
echo -e "${GREEN}--- PRD Project Bucket ---${NC}"
gcloud config set project "${PRD_PROJECT_ID}"
create_bucket "${PRD_PROJECT_ID}" "${PRD_BUCKET}" "${REGION}"

echo -e "${GREEN}=== Bootstrap Complete ===${NC}"
echo ""
echo -e "${GREEN}Bucket names for backend.conf files:${NC}"
echo "DEV: ${DEV_BUCKET}"
echo "PRD: ${PRD_BUCKET}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify backend.conf files have correct bucket names:"
echo "   - infrastructure/terraform/environments/dev/backend.conf"
echo "   - infrastructure/terraform/environments/prd/backend.conf"
echo "2. Run: terraform init -backend-config=environments/dev/backend.conf"
echo ""

