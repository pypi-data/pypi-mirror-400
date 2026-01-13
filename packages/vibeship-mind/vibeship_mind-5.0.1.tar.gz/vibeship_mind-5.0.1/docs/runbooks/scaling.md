# Scaling Runbook

## Horizontal Scaling

### API Scaling

**Manual scaling:**
```bash
# Scale to 5 replicas
kubectl scale deployment mind-api -n mind --replicas=5

# Verify
kubectl get pods -n mind -l app=mind-api
```

**HPA is enabled by default** - scales 3-20 based on CPU/memory.

### Database Scaling

**PostgreSQL read replicas:**
```bash
# Add read replica via Helm
helm upgrade mind ./deploy/helm/mind   --set postgresql.readReplicas.replicaCount=2
```

**Qdrant sharding:**
```bash
# Create sharded collection
curl -X PUT http://qdrant:6333/collections/memories_sharded   -H "Content-Type: application/json"   -d '{
    "vectors": {"size": 1536, "distance": "Cosine"},
    "shard_number": 4
  }'
```

## Vertical Scaling

### Increase API resources:
```bash
kubectl patch deployment mind-api -n mind -p '{
  "spec": {"template": {"spec": {"containers": [{
    "name": "api",
    "resources": {
      "requests": {"cpu": "500m", "memory": "1Gi"},
      "limits": {"cpu": "2000m", "memory": "4Gi"}
    }
  }]}}}
}'
```

### Increase database resources:
```bash
# Update StatefulSet
kubectl patch statefulset postgres -n mind -p '{
  "spec": {"template": {"spec": {"containers": [{
    "name": "postgres",
    "resources": {"limits": {"memory": "8Gi"}}
  }]}}}
}'
```

## Load Testing

```bash
# Run load test
k6 run --vus 100 --duration 5m scripts/load-test.js

# Monitor during test
watch kubectl top pods -n mind
```

## Capacity Planning

| Metric | Current | Alert | Scale Action |
|--------|---------|-------|--------------|
| API CPU | <70% | 80% | Add replica |
| API Memory | <70% | 85% | Increase limit |
| DB Connections | <80% | 90% | Add pooler |
| Qdrant Memory | <70% | 80% | Add shard |
| Event Lag | <1000 | 5000 | Add consumer |
