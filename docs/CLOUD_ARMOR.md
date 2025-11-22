# Cloud Armor - Proteção DDoS

## Visão Geral

O Cloud Armor foi configurado para proteger tanto o ambiente DEV quanto PRD contra ataques DDoS e outros tipos de ataques.

## Arquitetura

```
Internet → Load Balancer → Cloud Armor Security Policy → Backend Service → Cloud Run
```

### Componentes

1. **Load Balancer HTTP(S)**: Recebe todo o tráfego
2. **Cloud Armor Security Policy**: Aplica regras de segurança
3. **Backend Service**: Roteia tráfego para Cloud Run
4. **Cloud Run**: Aplicação

## Proteções Implementadas

### 1. Rate Limiting (Proteção DDoS)

- **DEV**: 200 requisições por minuto por IP
- **PRD**: 100 requisições por minuto por IP

Quando o limite é excedido:
- Retorna HTTP 429 (Too Many Requests)
- IP é temporariamente bloqueado

### 2. Adaptive Protection (PRD apenas)

- **Layer 7 DDoS Defense**: Proteção automática contra ataques DDoS de camada 7
- **Machine Learning**: Detecta padrões de ataque automaticamente
- **Custo**: Habilitado apenas em PRD para economizar custos em DEV

### 3. IP Allow/Block Lists (Opcional)

- **Allowed IPs**: IPs que podem bypassar rate limiting
- **Blocked IPs**: IPs permanentemente bloqueados

## Configuração por Ambiente

### DEV (Desenvolvimento)

```hcl
cloud_armor_enable = true
cloud_armor_rate_limit_requests = 200
cloud_armor_rate_limit_interval = 60
cloud_armor_enable_adaptive_protection = false  # Desabilitado para economizar
cloud_armor_enable_ssl = false
```

**Características:**
- Limites mais permissivos (200 req/min)
- Adaptive Protection desabilitado
- Foco em desenvolvimento e testes

### PRD (Produção)

```hcl
cloud_armor_enable = true
cloud_armor_rate_limit_requests = 100
cloud_armor_rate_limit_interval = 60
cloud_armor_enable_adaptive_protection = true  # Habilitado para máxima proteção
cloud_armor_enable_ssl = false  # Configure se tiver certificado SSL
```

**Características:**
- Limites mais restritivos (100 req/min)
- Adaptive Protection habilitado
- Máxima proteção contra DDoS

## URLs de Acesso

### Cloud Run Direto (NÃO Protegido)

```
https://<SERVICE_NAME>-xxxxx-<REGION>.a.run.app
```

⚠️ **Não use em produção!** Esta URL não passa pelo Cloud Armor.

### Load Balancer (PROTEGIDO - Use este!)

```
http://<LOAD_BALANCER_IP>
```

✅ **Use esta URL em produção!** Todo tráfego passa pelo Cloud Armor.

Para obter o IP do Load Balancer:
```bash
terraform output load_balancer_ip
```

## Configuração Avançada

### Bloquear IPs Específicos

Adicione no `terraform.tfvars`:

```hcl
cloud_armor_blocked_ips = [
  "<IP_ADDRESS>/32",      # Exemplo: "192.168.1.100/32"
  "<CIDR_BLOCK>"          # Exemplo: "10.0.0.0/24"
]
```

### Permitir IPs Específicos (Bypass Rate Limit)

Adicione no `terraform.tfvars`:

```hcl
cloud_armor_allowed_ips = [
  "<IP_ADDRESS>/32"  # Exemplo: "203.0.113.0/32" (IP da sua empresa)
]
```

### Habilitar SSL/HTTPS

1. Crie um certificado SSL no GCP:
   ```bash
   gcloud compute ssl-certificates create <CERT_NAME> \
     --domains=<YOUR_DOMAIN> \
     --global
   ```

2. Atualize `terraform.tfvars`:
   ```hcl
   cloud_armor_enable_ssl = true
   cloud_armor_ssl_certificate_id = "<CERT_NAME>"
   ```

3. Configure DNS para apontar para o Load Balancer IP

### Habilitar CDN

Para cachear conteúdo estático:

```hcl
cloud_armor_enable_cdn = true
```

## Monitoramento

### Logs do Cloud Armor

Acesse: https://console.cloud.google.com/logs/query

Filtros úteis:
```
resource.type="http_load_balancer"
jsonPayload.enforcedSecurityPolicy.name="<SERVICE_NAME>-armor-policy-<ENVIRONMENT>"
```

### Métricas

Acesse: https://console.cloud.google.com/monitoring

Métricas importantes:
- `loadbalancing.googleapis.com/https/request_count`
- `loadbalancing.googleapis.com/https/backend_request_count`
- `loadbalancing.googleapis.com/https/response_code_count`

## Troubleshooting

### Erro 429 (Too Many Requests)

**Causa**: Rate limit excedido

**Solução**:
1. Aguarde alguns minutos
2. Ajuste `cloud_armor_rate_limit_requests` se necessário
3. Adicione seu IP em `cloud_armor_allowed_ips` para bypass

### Load Balancer não responde

**Verificação**:
```bash
# Verificar se o Load Balancer foi criado
gcloud compute forwarding-rules list --global

# Verificar IP
terraform output load_balancer_ip

# Testar conectividade
curl -v http://$(terraform output -raw load_balancer_ip)
```

### Cloud Armor bloqueando tráfego legítimo

**Solução**:
1. Verifique logs do Cloud Armor
2. Ajuste rate limits se necessário
3. Adicione IPs legítimos em `cloud_armor_allowed_ips`

## Custos

### Cloud Armor

- **Security Policies**: $5/mês por política
- **Rules**: $1/mês por regra (primeiras 5 regras são gratuitas)
- **Adaptive Protection**: $3,000/mês (habilitado apenas em PRD)

### Load Balancer

- **Forwarding Rules**: $18/mês por regra
- **Backend Service**: Gratuito
- **Egress**: $0.12/GB (primeiros 10GB/mês gratuitos)

**Estimativa mensal:**
- **DEV**: ~$25/mês (sem Adaptive Protection)
- **PRD**: ~$3,025/mês (com Adaptive Protection)

## Recomendações

1. **Use sempre o Load Balancer URL** em produção (não o Cloud Run direto)
2. **Configure SSL/HTTPS** para produção
3. **Monitore logs** regularmente para detectar ataques
4. **Ajuste rate limits** baseado em tráfego real
5. **Use Adaptive Protection** apenas em PRD (economiza custos)

## Próximos Passos

1. Configure DNS para apontar para o Load Balancer IP
2. Configure SSL certificate se necessário
3. Monitore métricas e ajuste configurações
4. Revise logs regularmente para detectar padrões de ataque

