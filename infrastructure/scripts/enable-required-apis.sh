#!/bin/bash
# Script to enable all required GCP APIs for the project
#
# Usage: ./infrastructure/scripts/enable-required-apis.sh [PROJECT_ID]
# If PROJECT_ID is not provided, enables for both DEV and PRD

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project IDs
DEV_PROJECT_ID="payments-agent-wpp-dev"
PRD_PROJECT_ID="payments-agent-wpp"

# Required APIs
APIS=(
    "iamcredentials.googleapis.com"
    "iam.googleapis.com"
    "secretmanager.googleapis.com"
    "run.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "artifactregistry.googleapis.com"
    "storage.googleapis.com"
)

# Function to enable APIs for a project
enable_apis_for_project() {
    local project_id=$1
    echo -e "${BLUE}Enabling APIs for project: ${project_id}${NC}"
    gcloud config set project "${project_id}"
    
    for api in "${APIS[@]}"; do
        echo -e "${YELLOW}Enabling ${api}...${NC}"
        gcloud services enable "${api}" --project="${project_id}" || true
    done
    
    echo -e "${GREEN}✓ All APIs enabled for ${project_id}${NC}"
    echo ""
}

# Main execution
if [ -z "$1" ]; then
    # Enable for both projects
    echo -e "${GREEN}=== Enable Required GCP APIs ===${NC}"
    echo ""
    
    enable_apis_for_project "${DEV_PROJECT_ID}"
    enable_apis_for_project "${PRD_PROJECT_ID}"
    
    echo -e "${GREEN}=== Complete ===${NC}"
else
    # Enable for specified project
    enable_apis_for_project "$1"
fi

