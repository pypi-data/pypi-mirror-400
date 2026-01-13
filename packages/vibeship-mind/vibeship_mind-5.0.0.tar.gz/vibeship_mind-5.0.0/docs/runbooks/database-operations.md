# Database Operations Runbook

## PostgreSQL Operations

### Backup

**Manual Backup:**
```bash
# Create backup
kubectl exec -n mind postgres-0 -- pg_dump -U mind mind | gzip > backup-$(date +%Y%m%d).sql.gz

# Verify backup
gunzip -c backup-*.sql.gz | head -100
```

**Scheduled Backups:**
Backups run automatically via CronJob every 6 hours.

### Restore

```bash
# Stop API to prevent writes
kubectl scale deployment mind-api -n mind --replicas=0

# Restore from backup
gunzip -c backup-20241228.sql.gz | kubectl exec -i -n mind postgres-0 -- psql -U mind mind

# Restart API
kubectl scale deployment mind-api -n mind --replicas=3
```

### Schema Migration

```bash
# Run migrations
kubectl exec -n mind mind-api-xxx -- alembic upgrade head

# Check current version
kubectl exec -n mind mind-api-xxx -- alembic current

# Rollback one version
kubectl exec -n mind mind-api-xxx -- alembic downgrade -1
```

### Performance Tuning

**Check slow queries:**
```sql
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
```

**Vacuum and analyze:**
```bash
kubectl exec -n mind postgres-0 -- psql -U mind -c "VACUUM ANALYZE;"
```

## Qdrant Operations

### Collection Management

```bash
# List collections
kubectl exec -n mind qdrant-0 -- curl -s localhost:6333/collections

# Get collection info
kubectl exec -n mind qdrant-0 -- curl -s localhost:6333/collections/memories

# Create snapshot
kubectl exec -n mind qdrant-0 -- curl -X POST localhost:6333/collections/memories/snapshots
```

### Reindexing

```bash
# Trigger reindex via API
curl -X POST http://mind-api:8080/admin/reindex   -H "Authorization: Bearer $ADMIN_TOKEN"
```

## FalkorDB Operations

### Graph Queries

```bash
# Connect to FalkorDB
kubectl exec -it -n mind falkordb-0 -- redis-cli

# List graphs
GRAPH.LIST

# Query causal graph
GRAPH.QUERY causal_graph "MATCH (n) RETURN count(n)"
```

### Backup Graph

```bash
# Save RDB snapshot
kubectl exec -n mind falkordb-0 -- redis-cli BGSAVE

# Copy snapshot
kubectl cp mind/falkordb-0:/data/dump.rdb ./falkordb-backup.rdb
```
