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

# Note: Cloud DNS API should be enabled in the workflow before this script runs
# This is just a verification step
echo -e "${YELLOW}Verifying Cloud DNS API is enabled...${NC}"
if gcloud services list --enabled --project="${PROJECT_ID}" --filter="name:dns.googleapis.com" --format="value(name)" | grep -q "dns.googleapis.com"; then
    echo -e "${GREEN}✓ Cloud DNS API is enabled${NC}"
else
    echo -e "${YELLOW}⚠ Cloud DNS API may not be enabled yet${NC}"
    echo -e "${YELLOW}  Attempting to enable...${NC}"
    gcloud services enable dns.googleapis.com --project="${PROJECT_ID}" || {
        echo -e "${RED}✗ Failed to enable Cloud DNS API${NC}"
        echo -e "${YELLOW}  This may require manual enablement or additional permissions${NC}"
        echo -e "${YELLOW}  Service account needs: roles/serviceusage.serviceUsageAdmin${NC}"
    }
fi
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

# Grant DNS Admin permissions to GitHub Actions service account (if not already granted)
# Note: This should ideally be done in bootstrap-wif-dev.sh, but we check here as a fallback
echo -e "${YELLOW}Verifying DNS Admin permissions for GitHub Actions service account...${NC}"
# Check if service account has the role
HAS_DNS_ADMIN=$(gcloud projects get-iam-policy "${PROJECT_ID}" \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT} AND bindings.role:roles/dns.admin" \
    --format="value(bindings.role)" 2>/dev/null | grep -c "roles/dns.admin" || echo "0")

if [ "$HAS_DNS_ADMIN" -gt 0 ]; then
    echo -e "${GREEN}✓ Service account already has roles/dns.admin${NC}"
else
    echo -e "${YELLOW}⚠ Service account does not have roles/dns.admin${NC}"
    echo -e "${YELLOW}  Attempting to grant...${NC}"
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/dns.admin" \
        --condition=None \
        || {
        echo -e "${RED}✗ Failed to grant roles/dns.admin${NC}"
        echo -e "${YELLOW}  The service account needs roles/dns.admin to create DNS zones.${NC}"
        echo -e "${YELLOW}  Please run bootstrap-wif-dev.sh again or manually grant the role:${NC}"
        echo -e "${YELLOW}  gcloud projects add-iam-policy-binding ${PROJECT_ID} \\${NC}"
        echo -e "${YELLOW}    --member='serviceAccount:${SERVICE_ACCOUNT}' \\${NC}"
        echo -e "${YELLOW}    --role='roles/dns.admin'${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ DNS Admin permissions granted${NC}"
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

