# Incident Response Runbook

## Overview
This runbook covers incident response procedures for Mind v5 production systems.

## Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| P1 | Critical - Service down | 15 min | API unresponsive, data loss |
| P2 | Major - Degraded | 1 hour | High latency, partial outage |
| P3 | Minor - Limited impact | 4 hours | Single component issue |
| P4 | Low - Minimal impact | 24 hours | Non-critical bug |

## Escalation Path

1. On-call engineer (PagerDuty)
2. Team lead
3. Engineering manager
4. CTO (P1 only)

## Common Incidents

### API Unresponsive (P1)

**Symptoms:**
- Health checks failing
- 5xx error rate > 10%
- Latency > 10s

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n mind -l app=mind-api

# Check logs
kubectl logs -n mind -l app=mind-api --tail=100

# Check resource usage
kubectl top pods -n mind
```

**Resolution:**
1. If OOM: Scale up memory limits or add replicas
2. If CPU: Check for runaway queries, scale horizontally
3. If network: Check ingress, service mesh status
4. If database: See Database Issues section

**Rollback:**
```bash
# Rollback to previous deployment
kubectl rollout undo deployment/mind-api -n mind

# Verify rollback
kubectl rollout status deployment/mind-api -n mind
```

### Database Connection Exhaustion (P2)

**Symptoms:**
- "connection pool exhausted" errors
- Slow query responses
- Timeout errors

**Diagnosis:**
```bash
# Check connection count
kubectl exec -n mind postgres-0 -- psql -U mind -c "SELECT count(*) FROM pg_stat_activity;"

# Check long-running queries
kubectl exec -n mind postgres-0 -- psql -U mind -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY duration DESC LIMIT 10;"
```

**Resolution:**
1. Kill long-running queries if safe
2. Increase connection pool size
3. Add read replicas for read-heavy workloads
4. Review and optimize slow queries

### Memory Retrieval Latency (P2)

**Symptoms:**
- `/api/v1/memories` latency > 500ms
- Qdrant timeouts
- High embedding service latency

**Diagnosis:**
```bash
# Check Qdrant status
kubectl exec -n mind qdrant-0 -- curl -s localhost:6333/collections

# Check embedding cache hit rate
curl -s http://mind-api:8080/metrics | grep embedding_cache
```

**Resolution:**
1. If cache miss rate high: Warm cache, increase cache size
2. If Qdrant slow: Check collection size, add shards
3. If embedding slow: Check OpenAI rate limits, add caching

### Event Processing Backlog (P3)

**Symptoms:**
- NATS consumer lag increasing
- Delayed memory updates
- Stale decision outcomes

**Diagnosis:**
```bash
# Check NATS stream info
kubectl exec -n mind nats-0 -- nats stream info MIND_EVENTS

# Check consumer lag
kubectl exec -n mind nats-0 -- nats consumer info MIND_EVENTS gardener
```

**Resolution:**
1. Scale up consumer replicas
2. Check for processing errors in consumer logs
3. Increase batch size if processing is I/O bound

## Post-Incident

1. Create incident report within 24 hours
2. Schedule blameless postmortem for P1/P2
3. Create follow-up tickets for improvements
4. Update runbooks with new learnings
