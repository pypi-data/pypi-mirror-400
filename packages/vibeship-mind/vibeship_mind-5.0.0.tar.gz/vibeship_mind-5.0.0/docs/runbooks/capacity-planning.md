# Mind v5 Capacity Planning Guide

> **Last Updated**: December 28, 2025
> **Owner**: Platform Team
> **Review Cycle**: Quarterly

---

## Overview

This guide provides capacity planning guidance for Mind v5, including resource requirements, scaling thresholds, and growth projections.

---

## Current Capacity Profile

### Baseline Metrics (Production)

| Metric | Current | Peak | Headroom |
|--------|---------|------|----------|
| API Requests/sec | 500 | 1,200 | 140% |
| Memory Creations/min | 150 | 400 | 167% |
| Decision Tracks/min | 100 | 250 | 150% |
| Event Processing/sec | 800 | 2,000 | 150% |
| Embeddings Generated/min | 75 | 200 | 167% |

### Resource Utilization

| Component | CPU Util | Memory Util | Storage | IOPS |
|-----------|----------|-------------|---------|------|
| API (5 pods) | 35% | 45% | N/A | N/A |
| Worker (3 pods) | 40% | 50% | N/A | N/A |
| PostgreSQL | 25% | 60% | 150 GB | 2,000 |
| FalkorDB | 20% | 40% | 10 GB | 500 |
| Qdrant | 15% | 70% | 80 GB | 1,000 |
| NATS | 10% | 20% | 5 GB | 3,000 |

---

## Component Sizing Guidelines

### API Server

```yaml
# Per-pod requirements
resources:
  requests:
    cpu: "500m"      # 0.5 vCPU
    memory: "1Gi"    # 1 GiB RAM
  limits:
    cpu: "2000m"     # 2 vCPU
    memory: "4Gi"    # 4 GiB RAM

# Scaling formula
pods_needed = ceil(requests_per_second / 200)  # ~200 RPS per pod

# Example:
# 1,000 RPS → 5 pods
# 2,000 RPS → 10 pods
# 5,000 RPS → 25 pods
```

### Worker (Temporal)

```yaml
# Per-pod requirements
resources:
  requests:
    cpu: "250m"
    memory: "512Mi"
  limits:
    cpu: "1000m"
    memory: "2Gi"

# Scaling formula
pods_needed = ceil(workflows_per_minute / 100)  # ~100 workflows/min per worker

# Example:
# 500 workflows/min → 5 pods
# 1,000 workflows/min → 10 pods
```

### PostgreSQL

```
# Sizing guidelines based on event volume

Events/day    | Storage/month | RAM Required | vCPUs
------------- | ------------- | ------------ | ------
< 1M          | 10 GB         | 8 GB         | 2
1M - 10M      | 100 GB        | 32 GB        | 4
10M - 100M    | 1 TB          | 64 GB        | 8
100M - 1B     | 10 TB         | 128 GB       | 16

# Connection pool sizing
max_connections = (api_pods * 10) + (worker_pods * 5) + 20  # overhead

# Example: 5 API + 3 workers = 85 connections
```

### Qdrant (Vector Store)

```
# Sizing based on memory vectors

Vectors      | RAM Required | Storage | Recommended Instance
------------ | ------------ | ------- | --------------------
< 100K       | 2 GB         | 2 GB    | 2 vCPU, 4 GB RAM
100K - 1M    | 8 GB         | 20 GB   | 4 vCPU, 16 GB RAM
1M - 10M     | 32 GB        | 200 GB  | 8 vCPU, 64 GB RAM
10M - 100M   | 128 GB       | 2 TB    | 16 vCPU, 256 GB RAM

# Formula for memory (1536-dim OpenAI embeddings):
ram_gb = (num_vectors * 1536 * 4 bytes * 1.5 overhead) / 1e9
```

### FalkorDB (Graph)

```
# Sizing based on graph size

Nodes/Edges  | RAM Required | Storage | vCPUs
------------ | ------------ | ------- | ------
< 100K       | 2 GB         | 1 GB    | 1
100K - 1M    | 8 GB         | 10 GB   | 2
1M - 10M     | 32 GB        | 100 GB  | 4
10M - 100M   | 128 GB       | 1 TB    | 8

# Graph should fit in memory for optimal performance
```

### NATS JetStream

```
# Sizing based on message throughput

Messages/sec | RAM Required | Storage/day | vCPUs
------------ | ------------ | ----------- | ------
< 1K         | 512 MB       | 5 GB        | 1
1K - 10K     | 2 GB         | 50 GB       | 2
10K - 100K   | 8 GB         | 500 GB      | 4
100K - 1M    | 32 GB        | 5 TB        | 8
```

---

## Scaling Thresholds

### Automatic Scaling (HPA)

```yaml
# API Server HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mind-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mind-api
  minReplicas: 5
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 4
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
```

### Manual Scaling Triggers

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| API CPU | 70% | 85% | Scale pods |
| API Memory | 75% | 90% | Scale pods |
| PostgreSQL CPU | 60% | 80% | Upgrade instance |
| PostgreSQL Connections | 70% | 90% | Increase pool / upgrade |
| PostgreSQL Storage | 70% | 85% | Add storage |
| Qdrant Memory | 70% | 85% | Upgrade instance |
| NATS Storage | 60% | 80% | Add storage |

---

## Growth Projections

### User Growth Model

```
Current users: 10,000
Monthly growth rate: 15%

Projected users:
- 3 months:  15,000
- 6 months:  22,000
- 12 months: 45,000
- 24 months: 200,000
```

### Resource Growth Model

```python
# Memory growth per user (average)
memories_per_user_per_month = 50
avg_memory_size_bytes = 2000  # 2 KB including embeddings reference
embedding_size_bytes = 6144    # 1536 dims * 4 bytes

monthly_storage_per_user = (
    memories_per_user_per_month *
    (avg_memory_size_bytes + embedding_size_bytes)
)
# = 50 * 8144 = 407 KB/user/month

# For 100,000 users:
# Monthly storage growth = 100,000 * 407 KB = 40 GB/month
```

### Infrastructure Cost Projection

| Timeframe | Users | API Pods | PostgreSQL | Qdrant | Est. Cost/mo |
|-----------|-------|----------|------------|--------|--------------|
| Current | 10K | 5 | db.r6g.large | r6g.large | $2,500 |
| +6 months | 22K | 8 | db.r6g.xlarge | r6g.xlarge | $4,000 |
| +12 months | 45K | 15 | db.r6g.2xlarge | r6g.2xlarge | $8,000 |
| +24 months | 200K | 30 | db.r6g.4xlarge | r6g.4xlarge | $20,000 |

---

## Capacity Planning Checklist

### Monthly Review

- [ ] Review current utilization metrics
- [ ] Check growth rate vs projections
- [ ] Review HPA scaling events
- [ ] Identify approaching thresholds
- [ ] Update cost forecasts

### Quarterly Planning

- [ ] Review growth projections accuracy
- [ ] Plan infrastructure upgrades
- [ ] Update capacity documentation
- [ ] Review and optimize resource allocation
- [ ] Load test with projected traffic

---

## Bottleneck Analysis

### Common Bottlenecks

1. **PostgreSQL Connections**
   - Symptom: Connection timeout errors
   - Solution: Increase pool size, add PgBouncer, upgrade instance

2. **Embedding Generation**
   - Symptom: High OpenAI API latency
   - Solution: Increase cache size, batch requests, use smaller model

3. **Vector Search**
   - Symptom: Slow memory retrieval
   - Solution: Add Qdrant replicas, optimize indexes, reduce top_k

4. **Event Processing Backlog**
   - Symptom: Growing NATS consumer lag
   - Solution: Add worker pods, optimize consumers, increase batch size

### Performance Testing

```bash
# Load test API
k6 run --vus 100 --duration 5m scripts/load-tests/api-stress.js

# Benchmark memory retrieval
python scripts/benchmarks/retrieval_benchmark.py \
    --queries 1000 \
    --concurrency 50

# Database query analysis
psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

---

## Cost Optimization

### Reserved Instances

| Component | On-Demand | 1-Year RI | 3-Year RI | Savings |
|-----------|-----------|-----------|-----------|---------|
| API (c6g.xlarge) | $120/mo | $80/mo | $50/mo | 33-58% |
| PostgreSQL | $500/mo | $350/mo | $200/mo | 30-60% |
| Qdrant | $300/mo | $200/mo | $120/mo | 33-60% |

### Spot Instances

```yaml
# API can tolerate spot instances (stateless)
nodeSelector:
  node.kubernetes.io/instance-type: c6g.xlarge
tolerations:
  - key: "spot"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"

# Savings: Up to 70% vs on-demand
```

### Storage Tiering

```
# Move old data to cheaper storage
Events > 90 days → S3 Standard-IA
Events > 365 days → S3 Glacier
Backups > 30 days → S3 Glacier Deep Archive
```

---

## Monitoring Dashboards

### Key Capacity Metrics

- Grafana Dashboard: `/d/mind-capacity`
- Prometheus Queries:

```promql
# API capacity utilization
sum(rate(mind_http_requests_total[5m])) /
  (count(kube_pod_status_ready{pod=~"mind-api.*", condition="true"}) * 200)

# PostgreSQL connection utilization
pg_stat_activity_count / pg_settings_max_connections

# Qdrant memory utilization
qdrant_memory_usage_bytes / qdrant_memory_limit_bytes

# NATS stream storage
nats_jetstream_stream_bytes{stream="MIND_EVENTS"} / 10737418240  # 10GB limit
```

---

## Appendix

### A. Instance Type Comparison

| Instance | vCPU | RAM | Network | Use Case |
|----------|------|-----|---------|----------|
| c6g.large | 2 | 4 GB | Up to 10 Gbps | Small API |
| c6g.xlarge | 4 | 8 GB | Up to 10 Gbps | Medium API |
| c6g.2xlarge | 8 | 16 GB | Up to 10 Gbps | Large API |
| r6g.large | 2 | 16 GB | Up to 10 Gbps | Small DB |
| r6g.xlarge | 4 | 32 GB | Up to 10 Gbps | Medium DB |
| r6g.2xlarge | 8 | 64 GB | Up to 10 Gbps | Large DB |

### B. Related Documents

- [Scaling Runbook](./scaling.md)
- [Database Operations](./database-operations.md)
- [Disaster Recovery](./disaster-recovery.md)
