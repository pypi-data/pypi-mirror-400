# Mind v5 Deployment Guide

Production deployment guide for Mind v5 decision intelligence system.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  mind-api   │  │  gardener   │  │     temporal            │ │
│  │  (5 pods)   │  │  (3 pods)   │  │  (workflow engine)      │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
│         │                │                      │               │
│         └────────────────┴──────────────────────┘               │
│                          │                                       │
│  ┌───────────────────────┴───────────────────────────────────┐  │
│  │                    Data Layer                              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │ postgres │ │  qdrant  │ │ falkordb │ │   nats   │     │  │
│  │  │(pgvector)│ │ (vector) │ │ (graph)  │ │ (events) │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Kubernetes cluster** (1.28+)
   - EKS, GKE, AKS, or self-managed
   - Minimum: 3 nodes, 4 vCPU, 16GB RAM each

2. **Tools installed**
   ```bash
   # kubectl
   curl -LO "https://dl.k8s.io/release/v1.29.0/bin/linux/amd64/kubectl"

   # kustomize (optional, kubectl has built-in support)
   curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
   ```

3. **Container registry access**
   - Push access to ghcr.io or your registry

### Deploy to Staging

```bash
# 1. Build and push image
docker build -t ghcr.io/your-org/mind-api:latest .
docker push ghcr.io/your-org/mind-api:latest

# 2. Create namespace and secrets
kubectl create namespace mind-staging

kubectl create secret generic mind-secrets \
  --namespace=mind-staging \
  --from-literal=postgres-user="mind" \
  --from-literal=postgres-password="$(openssl rand -base64 32)" \
  --from-literal=jwt-secret="$(openssl rand -base64 32)" \
  --from-literal=openai-api-key="sk-your-key" \
  --from-literal=encryption-key="$(openssl rand -base64 32)" \
  --from-literal=signing-key="$(openssl rand -base64 32)"

# 3. Deploy
kubectl apply -k deploy/k8s/overlays/staging/

# 4. Verify
kubectl get pods -n mind-staging
kubectl rollout status deployment/mind-api -n mind-staging
```

### Deploy to Production

```bash
# 1. Create namespace
kubectl create namespace mind-production

# 2. Set up External Secrets Operator (recommended)
# See: https://external-secrets.io/latest/

# 3. Deploy
kubectl apply -k deploy/k8s/overlays/production/

# 4. Verify
kubectl get pods -n mind-production
kubectl rollout status deployment/prod-mind-api -n mind-production
kubectl rollout status deployment/prod-mind-gardener -n mind-production
```

## Directory Structure

```
deploy/
├── k8s/
│   ├── base/                    # Base manifests
│   │   ├── kustomization.yaml   # Kustomize config
│   │   ├── namespace.yaml       # Namespace definition
│   │   ├── configmap.yaml       # Environment config
│   │   ├── deployment.yaml      # API deployment
│   │   ├── service.yaml         # API service
│   │   ├── gardener-*.yaml      # Gardener worker
│   │   ├── postgres.yaml        # PostgreSQL + pgvector
│   │   ├── qdrant.yaml          # Vector search
│   │   ├── falkordb.yaml        # Graph database
│   │   ├── nats.yaml            # Event backbone
│   │   ├── temporal.yaml        # Workflow engine
│   │   ├── hpa.yaml             # Autoscaling
│   │   ├── pdb.yaml             # Pod disruption budget
│   │   └── ingress.yaml         # Ingress rules
│   │
│   └── overlays/
│       ├── staging/             # Staging overrides
│       │   ├── kustomization.yaml
│       │   ├── namespace.yaml
│       │   └── secrets.yaml
│       │
│       └── production/          # Production overrides
│           ├── kustomization.yaml
│           ├── namespace.yaml
│           ├── secrets.yaml
│           ├── network-policy.yaml
│           ├── pod-security-policy.yaml
│           └── service-monitor.yaml
│
├── helm/
│   └── mind/                    # Helm chart (alternative)
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── prometheus/                  # Monitoring
│   ├── prometheus.yaml
│   ├── alerts.yaml
│   └── alertmanager.yaml
│
├── grafana/                     # Dashboards
│   └── provisioning/
│       └── dashboards/
│
└── docker/                      # Local development
    └── docker-compose.observability.yaml
```

## Configuration

### Required Secrets

| Secret Key | Description |
|------------|-------------|
| `postgres-user` | PostgreSQL username |
| `postgres-password` | PostgreSQL password |
| `jwt-secret` | JWT signing secret (min 32 chars) |
| `openai-api-key` | OpenAI API key for embeddings |
| `encryption-key` | Data encryption key |
| `signing-key` | Request signing key |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MIND_ENV` | production | Environment name |
| `LOG_LEVEL` | INFO | Log verbosity |
| `POSTGRES_HOST` | postgres | Database host |
| `QDRANT_URL` | http://qdrant:6333 | Vector DB URL |
| `TEMPORAL_HOST` | temporal | Temporal host |
| `NATS_URL` | nats://nats:4222 | NATS URL |

## Monitoring

### Prometheus Metrics

Access metrics at `/metrics` on each service:
- `mind_requests_total` - Request count
- `mind_request_latency_seconds` - Request latency
- `mind_decision_success_rate` - Decision quality
- `mind_memory_retrieval_relevance` - Retrieval quality

### Grafana Dashboards

Import dashboards from `deploy/grafana/provisioning/dashboards/`:
- Mind Overview
- API Performance
- Memory Operations
- Gardener Workflows

### Alerts

Pre-configured alerts in `deploy/prometheus/alerts.yaml`:
- High error rate (>1%)
- High latency (p99 > 1s)
- Pod restarts
- Memory pressure

## Scaling

### Horizontal Pod Autoscaler

API scales 5-20 pods based on CPU/memory:
```yaml
minReplicas: 5
maxReplicas: 20
targetCPU: 70%
targetMemory: 80%
```

### Manual Scaling

```bash
# Scale API
kubectl scale deployment/prod-mind-api --replicas=10 -n mind-production

# Scale Gardener
kubectl scale deployment/prod-mind-gardener --replicas=5 -n mind-production
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n mind-production
kubectl describe pod <pod-name> -n mind-production
kubectl logs <pod-name> -n mind-production
```

### Check Services

```bash
kubectl get svc -n mind-production
kubectl port-forward svc/prod-mind-api 8080:80 -n mind-production
curl http://localhost:8080/health
```

### Database Connectivity

```bash
kubectl exec -it postgres-0 -n mind-production -- psql -U mind -d mind
```

### Temporal UI

```bash
kubectl port-forward svc/temporal-ui 8088:8080 -n mind-production
# Open http://localhost:8088
```

## Backup & Recovery

### PostgreSQL Backup

```bash
# Create backup
kubectl exec postgres-0 -n mind-production -- pg_dump -U mind mind > backup.sql

# Restore
kubectl exec -i postgres-0 -n mind-production -- psql -U mind mind < backup.sql
```

### Disaster Recovery

1. Restore PostgreSQL from backup
2. Qdrant and FalkorDB can be rebuilt from PostgreSQL events
3. NATS JetStream replays unprocessed events

## Security Checklist

- [ ] Secrets managed via External Secrets Operator
- [ ] Network policies applied
- [ ] Pod security policies enabled
- [ ] TLS enabled on ingress
- [ ] RBAC configured
- [ ] Image scanning in CI/CD
- [ ] No secrets in git history

## Support

- **Logs**: Structured JSON, ship to your logging platform
- **Metrics**: Prometheus-compatible, scrape `/metrics`
- **Traces**: OpenTelemetry, export to Tempo/Jaeger
