# Mind v5 Backup and Recovery Runbook

> **Last Updated**: December 28, 2025
> **Owner**: Platform Team
> **Review Cycle**: Quarterly

---

## Overview

This runbook covers backup procedures, recovery processes, and data protection for Mind v5 components. Mind v5 uses an event-sourced architecture, which provides natural replay capabilities but still requires regular backups for disaster recovery.

---

## Backup Strategy

### Components Requiring Backup

| Component | Data Type | Backup Method | Frequency | Retention |
|-----------|-----------|---------------|-----------|-----------|
| PostgreSQL | Events, memories, decisions | pg_dump / WAL archiving | Continuous + Daily | 30 days + 7 yearly |
| FalkorDB | Causal graph | RDB snapshots | Hourly | 7 days |
| Qdrant | Embeddings | Snapshots | Daily | 7 days |
| NATS JetStream | Event streams | Stream snapshots | Hourly | 3 days |
| Temporal | Workflow state | Namespace export | Daily | 30 days |
| Secrets (Vault) | Encryption keys | Vault snapshots | Daily | 90 days |

### Backup Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Backup Pipeline                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐  │
│   │PostgreSQL│────▶│ pgBackRest│────▶│   S3     │────▶│ Glacier  │  │
│   │  (WAL)   │     │  (incr)   │     │ (hot)    │     │ (archive)│  │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘  │
│                                                                      │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐                    │
│   │ FalkorDB │────▶│  BGSAVE  │────▶│   S3     │                    │
│   │          │     │  (RDB)   │     │ (hot)    │                    │
│   └──────────┘     └──────────┘     └──────────┘                    │
│                                                                      │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐                    │
│   │  Qdrant  │────▶│ Snapshot │────▶│   S3     │                    │
│   │          │     │  API     │     │ (hot)    │                    │
│   └──────────┘     └──────────┘     └──────────┘                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PostgreSQL Backup Procedures

### Continuous WAL Archiving (Primary Method)

```bash
# Verify WAL archiving is enabled
psql -c "SHOW archive_mode;"           # Should be 'on'
psql -c "SHOW archive_command;"        # Should point to pgbackrest

# Check archive status
pgbackrest info --stanza=mind

# Expected output:
# stanza: mind
#     status: ok
#     cipher: aes-256-cbc
#     db (current)
#         wal archive min/max (14): 000000010000000000000001/000000010000000100000042
```

### Daily Full Backup

```bash
# Trigger manual full backup (runs automatically at 02:00 UTC)
pgbackrest backup --stanza=mind --type=full

# Verify backup completed
pgbackrest info --stanza=mind --output=json | jq '.[] | .backup[-1]'

# Expected fields:
# - "type": "full"
# - "info": {"size": <bytes>, "delta": <bytes>}
# - "timestamp": {"start": ..., "stop": ...}
```

### Backup Verification

```bash
# Verify backup integrity (weekly automated check)
pgbackrest verify --stanza=mind

# Test restore to temp instance (monthly)
./scripts/backup/test-restore.sh --stanza=mind --target-time="2025-01-15 12:00:00"
```

---

## FalkorDB Backup Procedures

### RDB Snapshots

```bash
# Connect to FalkorDB
redis-cli -h falkordb -p 6379

# Trigger manual snapshot
BGSAVE

# Check save status
LASTSAVE  # Returns Unix timestamp of last save

# Verify RDB file
ls -la /data/dump.rdb
```

### Backup to S3

```bash
# Automated backup script (runs hourly via CronJob)
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BUCKET="mind-backups-production"

# Trigger save
redis-cli -h falkordb BGSAVE
sleep 10  # Wait for save to complete

# Copy to S3
aws s3 cp /data/dump.rdb s3://${BUCKET}/falkordb/${TIMESTAMP}/dump.rdb \
    --storage-class STANDARD_IA

# Cleanup old local snapshots
find /backups/falkordb -mtime +7 -delete
```

### Graph Export (Alternative)

```bash
# Export graph to Cypher format (for cross-version compatibility)
redis-cli -h falkordb GRAPH.QUERY mind_causal \
    "MATCH (n)-[r]->(m) RETURN n, r, m" > /backups/graph_export.cypher
```

---

## Qdrant Backup Procedures

### Snapshot API

```bash
# Create snapshot
curl -X POST "http://qdrant:6333/collections/mind_memories/snapshots"

# Response: {"result": {"name": "mind_memories-2025-01-15-12-00-00.snapshot"}}

# List snapshots
curl "http://qdrant:6333/collections/mind_memories/snapshots"

# Download snapshot for offsite storage
curl "http://qdrant:6333/collections/mind_memories/snapshots/mind_memories-2025-01-15-12-00-00.snapshot" \
    -o /backups/qdrant/mind_memories-2025-01-15.snapshot
```

### Full Collection Export

```bash
# For large collections, use scroll API with batching
python scripts/backup/export_qdrant.py \
    --collection mind_memories \
    --output /backups/qdrant/full_export.json \
    --batch-size 1000
```

---

## NATS JetStream Backup

### Stream Snapshots

```bash
# List streams
nats stream ls

# Get stream info
nats stream info MIND_EVENTS

# Create stream snapshot
nats stream backup MIND_EVENTS /backups/nats/MIND_EVENTS_$(date +%Y%m%d).tar.gz
```

### Consumer State Backup

```bash
# Export consumer states
nats consumer ls MIND_EVENTS --json > /backups/nats/consumers.json

# For each consumer, export position
for consumer in $(nats consumer ls MIND_EVENTS -n); do
    nats consumer info MIND_EVENTS $consumer --json >> /backups/nats/consumer_states.json
done
```

---

## Recovery Procedures

### PostgreSQL Point-in-Time Recovery

```bash
# 1. Stop the application
kubectl scale deployment mind-api --replicas=0 -n mind-production

# 2. Identify target recovery point
pgbackrest info --stanza=mind --output=json | jq '.[] | .backup'

# 3. Restore to specific point in time
pgbackrest restore --stanza=mind \
    --target="2025-01-15 14:30:00" \
    --target-action=promote \
    --type=time \
    --pg-path=/var/lib/postgresql/data

# 4. Start PostgreSQL and verify
pg_ctl start -D /var/lib/postgresql/data
psql -c "SELECT count(*) FROM events;"  # Verify event count

# 5. Restart application
kubectl scale deployment mind-api --replicas=5 -n mind-production
```

### FalkorDB Recovery

```bash
# 1. Stop FalkorDB
kubectl scale statefulset falkordb --replicas=0 -n mind-production

# 2. Download backup from S3
aws s3 cp s3://mind-backups-production/falkordb/20250115_120000/dump.rdb /data/dump.rdb

# 3. Start FalkorDB
kubectl scale statefulset falkordb --replicas=1 -n mind-production

# 4. Verify graph
redis-cli -h falkordb GRAPH.QUERY mind_causal "MATCH (n) RETURN count(n)"
```

### Qdrant Recovery

```bash
# 1. Delete existing collection (if corrupted)
curl -X DELETE "http://qdrant:6333/collections/mind_memories"

# 2. Restore from snapshot
curl -X PUT "http://qdrant:6333/collections/mind_memories/snapshots/recover" \
    -H "Content-Type: application/json" \
    -d '{"location": "file:///backups/qdrant/mind_memories-2025-01-15.snapshot"}'

# 3. Verify
curl "http://qdrant:6333/collections/mind_memories"
```

### Event Replay (Alternative Recovery)

Since Mind v5 uses event sourcing, you can rebuild any projection from events:

```bash
# 1. Connect to the replay API
curl -X POST "http://mind-api:8000/v1/admin/events/replay" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "from_sequence": 0,
        "projections": ["causal_graph", "memories", "patterns"]
    }'

# 2. Monitor replay progress
curl "http://mind-api:8000/v1/admin/events/replay/status"
```

---

## Backup Monitoring

### Prometheus Alerts

```yaml
# alerts/backup-alerts.yaml
groups:
  - name: backup_alerts
    rules:
      - alert: BackupFailed
        expr: backup_last_success_timestamp_seconds < time() - 86400
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "Backup has not succeeded in 24 hours"

      - alert: BackupSizeAnomaly
        expr: |
          abs(backup_size_bytes - backup_size_bytes offset 1d)
          / backup_size_bytes offset 1d > 0.5
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Backup size changed more than 50%"
```

### Backup Verification Checklist

- [ ] Daily: Check backup job status in monitoring
- [ ] Weekly: Verify backup integrity with checksums
- [ ] Monthly: Test restore to staging environment
- [ ] Quarterly: Full DR test with production data

---

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| On-Call Primary | - | PagerDuty |
| Database Admin | - | #db-ops Slack |
| Platform Lead | - | #platform Slack |

---

## Appendix: Backup Scripts

### Location
All backup scripts are in `/scripts/backup/`:
- `pg_backup.sh` - PostgreSQL backup wrapper
- `falkordb_backup.sh` - FalkorDB backup
- `qdrant_backup.py` - Qdrant snapshot and export
- `test-restore.sh` - Restore verification
- `verify-backups.sh` - Integrity checks

### Kubernetes CronJobs
Backup CronJobs are defined in:
- `deploy/k8s/overlays/production/cronjobs/backup-postgres.yaml`
- `deploy/k8s/overlays/production/cronjobs/backup-falkordb.yaml`
- `deploy/k8s/overlays/production/cronjobs/backup-qdrant.yaml`
