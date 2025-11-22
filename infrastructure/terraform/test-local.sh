#!/bin/bash
# Script para testar Terraform localmente antes de fazer commit
# Uso: ./test-local.sh [dev|prd]

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar argumentos
ENVIRONMENT="${1:-dev}"
PROJECT_ID="payments-agent-wpp-${ENVIRONMENT}"
REGION="us-central1"
SERVICE_NAME="payments-agent"

# Se for PRD, remover -prd do project_id
if [ "$ENVIRONMENT" == "prd" ]; then
    PROJECT_ID="payments-agent-wpp"
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Teste Local do Terraform - ${YELLOW}${ENVIRONMENT^^}${NC}${BLUE}                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Project ID: ${YELLOW}${PROJECT_ID}${NC}"
echo -e "Region: ${YELLOW}${REGION}${NC}"
echo -e "Service Name: ${YELLOW}${SERVICE_NAME}${NC}"
echo ""

# Navegar para o diretório correto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}✓ Diretório: ${SCRIPT_DIR}${NC}"
echo ""

# Verificar se terraform está instalado
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}✗ Terraform não está instalado${NC}"
    exit 1
fi

TERRAFORM_VERSION=$(terraform version | head -n 1)
echo -e "${GREEN}✓ ${TERRAFORM_VERSION}${NC}"
echo ""

# Verificar se gcloud está instalado e autenticado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗ gcloud não está instalado${NC}"
    exit 1
fi

echo -e "${YELLOW}Verificando autenticação GCP...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 &>/dev/null; then
    echo -e "${RED}✗ Não autenticado no GCP. Execute: gcloud auth login${NC}"
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
echo -e "${GREEN}✓ Autenticado como: ${ACTIVE_ACCOUNT}${NC}"

CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "not-set")
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠ Project configurado no gcloud: ${CURRENT_PROJECT}${NC}"
    echo -e "${YELLOW}  (Isso não afeta o Terraform, mas é bom estar no projeto correto)${NC}"
fi
echo ""

# Verificar se o secret existe e tem versão
echo -e "${YELLOW}Verificando Secret Manager Secret...${NC}"
SECRET_NAME="${SERVICE_NAME}-google-api-key"
SECRET_HAS_VERSION=false

if gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" &>/dev/null; then
    echo -e "${GREEN}✓ Secret existe: ${SECRET_NAME}${NC}"
    
    # Verificar se tem versão
    VERSION_COUNT=$(gcloud secrets versions list "$SECRET_NAME" --project="$PROJECT_ID" --filter="state:enabled" --format="value(name)" 2>/dev/null | wc -l)
    if [ "$VERSION_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Secret tem ${VERSION_COUNT} versão(ões) ativa(s)${NC}"
        SECRET_HAS_VERSION=true
    else
        echo -e "${YELLOW}⚠ Secret existe mas não tem versão ativa!${NC}"
        echo -e "${YELLOW}  Nota: Para terraform plan, isso é OK - o plan não valida versões de secret${NC}"
        echo -e "${YELLOW}  No workflow, a versão será criada ANTES do apply${NC}"
        SECRET_HAS_VERSION=false
    fi
else
    echo -e "${YELLOW}⚠ Secret não existe: ${SECRET_NAME}${NC}"
    echo -e "${YELLOW}  O Terraform criará o secret durante o apply${NC}"
    echo -e "${YELLOW}  Mas você precisará criar a versão ANTES do apply no workflow${NC}"
    SECRET_HAS_VERSION=false
fi

if [ "$SECRET_HAS_VERSION" = true ]; then
    echo -e "${GREEN}✓ Secret tem versão - terraform apply funcionará${NC}"
else
    echo -e "${YELLOW}⚠ Secret não tem versão - apenas terraform plan pode ser testado${NC}"
    echo -e "${YELLOW}  O workflow criará a versão ANTES do apply${NC}"
fi
echo ""

# Verificar se backend está configurado
echo -e "${YELLOW}Verificando backend GCS...${NC}"
BACKEND_BUCKET="payments-agent-wpp-${ENVIRONMENT}-tf-state"
if gsutil ls "gs://${BACKEND_BUCKET}" &>/dev/null; then
    echo -e "${GREEN}✓ Backend bucket existe: ${BACKEND_BUCKET}${NC}"
else
    echo -e "${RED}✗ Backend bucket não existe: ${BACKEND_BUCKET}${NC}"
    echo -e "${YELLOW}  Execute o bootstrap primeiro ou crie o bucket manualmente${NC}"
    exit 1
fi
echo ""

# Inicializar Terraform
echo -e "${YELLOW}Inicializando Terraform...${NC}"
if terraform init -backend-config=environments/${ENVIRONMENT}/backend.conf -input=false; then
    echo -e "${GREEN}✓ Terraform inicializado${NC}"
else
    echo -e "${RED}✗ Falha ao inicializar Terraform${NC}"
    exit 1
fi
echo ""

# Validar arquivos Terraform
echo -e "${YELLOW}Validando arquivos Terraform...${NC}"
if terraform validate; then
    echo -e "${GREEN}✓ Configuração Terraform válida${NC}"
else
    echo -e "${RED}✗ Erros de validação encontrados${NC}"
    exit 1
fi
echo ""

# Format check
echo -e "${YELLOW}Verificando formatação Terraform...${NC}"
if terraform fmt -check -recursive; then
    echo -e "${GREEN}✓ Formatação correta${NC}"
else
    echo -e "${YELLOW}⚠ Alguns arquivos não estão formatados corretamente${NC}"
    echo -e "${YELLOW}  Execute: terraform fmt -recursive${NC}"
    echo ""
    read -p "Deseja formatar automaticamente? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform fmt -recursive
        echo -e "${GREEN}✓ Arquivos formatados${NC}"
    fi
fi
echo ""

# Verificar state atual
echo -e "${YELLOW}Verificando state atual...${NC}"
if terraform state list &>/dev/null; then
    RESOURCE_COUNT=$(terraform state list | wc -l)
    echo -e "${GREEN}✓ State tem ${RESOURCE_COUNT} recursos${NC}"
    
    # Verificar se Cloud Run está no state
    if terraform state show google_cloud_run_v2_service.service &>/dev/null; then
        echo -e "${GREEN}✓ Cloud Run Service está no state${NC}"
    else
        echo -e "${YELLOW}⚠ Cloud Run Service não está no state (será criado)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ State vazio ou erro ao acessar${NC}"
fi
echo ""

# Verificar variáveis necessárias
echo -e "${YELLOW}Preparando variáveis...${NC}"

# Para testar, precisamos de uma imagem
# Usaremos uma imagem dummy se não fornecida
IMAGE_TAG="${2:-us-central1-docker.pkg.dev/payments-agent-wpp/docker-repo/agent:test}"

echo -e "Image: ${YELLOW}${IMAGE_TAG}${NC}"
echo -e "${BLUE}(Use: ./test-local.sh ${ENVIRONMENT} <image-tag> para especificar outra imagem)${NC}"
echo ""

# Executar terraform plan
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Executando Terraform Plan                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

TF_VAR_FILE="environments/${ENVIRONMENT}/terraform.tfvars"

# Verificar se o arquivo de variáveis existe
if [ ! -f "$TF_VAR_FILE" ]; then
    echo -e "${RED}✗ Arquivo de variáveis não encontrado: ${TF_VAR_FILE}${NC}"
    exit 1
fi

echo -e "${YELLOW}Executando: terraform plan -var-file=${TF_VAR_FILE} -var=\"image=${IMAGE_TAG}\"${NC}"
echo ""

if terraform plan \
    -var-file="$TF_VAR_FILE" \
    -var="image=${IMAGE_TAG}" \
    -detailed-exitcode; then
    
    PLAN_EXIT_CODE=$?
    
    if [ $PLAN_EXIT_CODE -eq 0 ]; then
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✓ Terraform Plan: Sem mudanças                      ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    elif [ $PLAN_EXIT_CODE -eq 2 ]; then
        echo ""
        echo -e "${YELLOW}╔════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║  ⚠ Terraform Plan: Mudanças planejadas               ║${NC}"
        echo -e "${YELLOW}╚════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${BLUE}Revise o plano acima cuidadosamente!${NC}"
        echo ""
        
        # Perguntar se deseja ver o resumo
        read -p "Deseja ver o resumo do plano? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            terraform plan \
                -var-file="$TF_VAR_FILE" \
                -var="image=${IMAGE_TAG}" \
                -compact-warnings 2>&1 | grep -E "^Plan:|^  \+|^  ~|^  -|^  ->" | head -50
        fi
    else
        echo -e "${RED}✗ Erro inesperado no terraform plan${NC}"
        exit 1
    fi
else
    PLAN_EXIT_CODE=$?
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ Terraform Plan: ERROS ENCONTRADOS                  ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}Corrija os erros antes de fazer commit!${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Resumo do Teste                                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Checklist final
echo -e "${YELLOW}Checklist:${NC}"
echo -e "  [✓] Terraform instalado e configurado"
echo -e "  [✓] Autenticação GCP verificada"
echo -e "  [✓] Backend GCS configurado"
echo -e "  [✓] Terraform inicializado"
echo -e "  [✓] Arquivos validados"
echo -e "  [✓] Terraform plan executado"

if [ $PLAN_EXIT_CODE -eq 0 ] || [ $PLAN_EXIT_CODE -eq 2 ]; then
    echo ""
    echo -e "${GREEN}✅ TERRAFORM ESTÁ PRONTO PARA COMMIT!${NC}"
    echo ""
    echo -e "${BLUE}Próximos passos:${NC}"
    echo -e "  1. Revise o plano acima (se houver mudanças)"
    echo -e "  2. Faça commit das mudanças"
    echo -e "  3. Push para o GitHub"
    echo -e "  4. O GitHub Actions executará o deploy"
else
    echo ""
    echo -e "${RED}❌ CORRIJA OS ERROS ANTES DE FAZER COMMIT!${NC}"
    exit 1
fi

echo ""

