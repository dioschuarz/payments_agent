#!/bin/bash
# Bootstrap script to create DNS zone in Cloud DNS (DEV project)
#
# Usage: ./scripts/bootstrap-dns-zone.sh
#
# This script creates a DNS zone in Google Cloud DNS for dscorpsolutions.com
# The zone is created once and shared by all agents (DEV and PRD)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# DNS Zone configuration
# PROJECT_ID can be overridden by environment variable (for GitHub Actions)
PROJECT_ID="${DEV_GCP_PROJECT_ID:-payments-agent-wpp-dev}"
ZONE_NAME="dscorpsolutions-zone"
DNS_NAME="dscorpsolutions.com"
DESCRIPTION="DNS zone for dscorpsolutions.com domain"
SERVICE_ACCOUNT="github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${GREEN}=== Bootstrap DNS Zone ===${NC}"
echo "Project: ${PROJECT_ID}"
echo "Zone Name: ${ZONE_NAME}"
echo "DNS Name: ${DNS_NAME}"
echo ""

# Set project
gcloud config set project "${PROJECT_ID}" || {
  echo -e "${RED}Failed to set project${NC}"
  exit 1
}

# Enable required API
echo -e "${YELLOW}Enabling Cloud DNS API...${NC}"
gcloud services enable dns.googleapis.com --project="${PROJECT_ID}" || {
  echo -e "${YELLOW}API may already be enabled or enabling failed${NC}"
}
echo -e "${GREEN}✓ Cloud DNS API enabled${NC}"
echo ""

# Check if zone already exists
echo -e "${YELLOW}Checking if DNS zone already exists...${NC}"
if gcloud dns managed-zones describe "${ZONE_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}DNS zone ${ZONE_NAME} already exists, skipping creation${NC}"
    EXISTING_ZONE=true
else
    echo -e "${YELLOW}DNS zone ${ZONE_NAME} does not exist, creating...${NC}"
    EXISTING_ZONE=false
fi
echo ""

# Create DNS zone if it doesn't exist
if [ "$EXISTING_ZONE" = false ]; then
    echo -e "${YELLOW}Creating DNS zone...${NC}"
    gcloud dns managed-zones create "${ZONE_NAME}" \
        --dns-name="${DNS_NAME}" \
        --description="${DESCRIPTION}" \
        --project="${PROJECT_ID}" \
        --visibility=public
    
    echo -e "${GREEN}✓ DNS zone created${NC}"
else
    echo -e "${GREEN}✓ Using existing DNS zone${NC}"
fi
echo ""

# Get zone details
echo -e "${YELLOW}Retrieving DNS zone information...${NC}"
ZONE_INFO=$(gcloud dns managed-zones describe "${ZONE_NAME}" --project="${PROJECT_ID}" --format="json")
ZONE_DNS=$(echo "$ZONE_INFO" | grep -o '"dnsName": "[^"]*' | cut -d'"' -f4)
NAME_SERVERS=$(echo "$ZONE_INFO" | grep -o '"nameServers": \[[^]]*\]' | grep -o '"[^"]*' | grep -v 'nameServers' | tr -d '"' | tr '\n' ' ')
echo ""

# Display nameservers (important for Google Domains configuration)
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  DNS Zone Information                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo -e "${GREEN}Zone Name:${NC} ${ZONE_NAME}"
echo -e "${GREEN}DNS Name:${NC} ${ZONE_DNS}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Configure these nameservers in your domain registrar${NC}"
echo -e "${YELLOW}   If using Google Domains, update the nameservers to:${NC}"
echo ""
echo "$NAME_SERVERS" | tr ' ' '\n' | while read -r ns; do
    if [ -n "$ns" ]; then
        echo -e "   ${GREEN}${ns}${NC}"
    fi
done
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo ""

# Grant DNS Admin permissions to GitHub Actions service account
echo -e "${YELLOW}Granting DNS Admin permissions to GitHub Actions service account...${NC}"
if gcloud projects get-iam-policy "${PROJECT_ID}" --flatten="bindings[].members" --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT} AND bindings.role:roles/dns.admin" --format="table(bindings.role)" &>/dev/null | grep -q "roles/dns.admin"; then
    echo -e "${YELLOW}Service account already has roles/dns.admin, skipping${NC}"
else
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/dns.admin" \
        --condition=None \
        || {
        echo -e "${YELLOW}Failed to grant roles/dns.admin. Service account may not exist yet.${NC}"
        echo -e "${YELLOW}Run bootstrap-wif-dev.sh first to create the service account.${NC}"
    }
    echo -e "${GREEN}✓ Permissions granted${NC}"
fi
echo ""

# Verify service account exists
echo -e "${YELLOW}Verifying service account exists...${NC}"
if gcloud iam service-accounts describe "${SERVICE_ACCOUNT}" --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${GREEN}✓ Service account exists${NC}"
else
    echo -e "${YELLOW}⚠ Service account does not exist yet${NC}"
    echo -e "${YELLOW}  Run bootstrap-wif-dev.sh first to create it${NC}"
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Bootstrap DNS Zone Complete                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Copy the nameservers shown above"
echo "  2. Configure them in your domain registrar (Google Domains)"
echo "  3. Wait for DNS propagation (5-60 minutes)"
echo "  4. Deploy via GitHub Actions - Terraform will create DNS A records automatically"
echo ""

