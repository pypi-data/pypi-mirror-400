# Mind v5 Disaster Recovery Plan

> **Last Updated**: December 28, 2025
> **Owner**: Platform Team
> **Classification**: Confidential
> **Review Cycle**: Semi-Annual

---

## Executive Summary

This document outlines the Disaster Recovery (DR) plan for Mind v5, including Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), and procedures for various disaster scenarios.

---

## Recovery Objectives

### Service Level Agreements

| Metric | Target | Maximum |
|--------|--------|---------|
| **RTO** (Recovery Time Objective) | 1 hour | 4 hours |
| **RPO** (Recovery Point Objective) | 5 minutes | 15 minutes |
| **Availability** | 99.9% | 99.5% |

### Component-Specific Objectives

| Component | RTO | RPO | Priority |
|-----------|-----|-----|----------|
| API Gateway | 15 min | N/A (stateless) | P1 |
| PostgreSQL | 30 min | 5 min (WAL) | P1 |
| NATS JetStream | 30 min | 1 min | P1 |
| FalkorDB | 1 hour | 1 hour | P2 |
| Qdrant | 2 hours | 24 hours | P3 |
| Temporal | 1 hour | 5 min | P2 |

---

## Disaster Scenarios

### Scenario 1: Single AZ Failure

**Impact**: Partial service degradation
**Probability**: Medium
**Detection**: CloudWatch/Prometheus alerts

**Response**:
1. Automatic failover via Kubernetes pod anti-affinity
2. Load balancer removes unhealthy targets
3. No manual intervention required

**Recovery Steps**:
```bash
# Verify pods redistributed
kubectl get pods -n mind-production -o wide

# Check service health
curl -s https://api.mind.dev/health | jq .

# Scale up if capacity reduced
kubectl scale deployment mind-api --replicas=10 -n mind-production
```

---

### Scenario 2: Complete Region Failure

**Impact**: Complete service outage
**Probability**: Low
**Detection**: External monitoring (Pingdom, Datadog Synthetics)

**Response**:
1. Initiate cross-region failover
2. DNS cutover to secondary region
3. Notify stakeholders

**Recovery Steps**:

```bash
# Phase 1: Verify secondary region readiness (5 min)
kubectl config use-context mind-dr-region
kubectl get pods -n mind-production

# Phase 2: Restore databases (30 min)
# PostgreSQL - restore from S3 cross-region replicated backup
./scripts/dr/restore-postgres.sh --region us-west-2 --target-time "latest"

# FalkorDB - restore from S3
./scripts/dr/restore-falkordb.sh --region us-west-2

# Phase 3: DNS cutover (5 min)
# Update Route53 to point to DR region
aws route53 change-resource-record-sets \
    --hosted-zone-id ${HOSTED_ZONE_ID} \
    --change-batch file://dns-failover.json

# Phase 4: Verify services (10 min)
./scripts/dr/verify-services.sh

# Phase 5: Notify stakeholders
./scripts/dr/send-status-update.sh "Failover complete, service restored"
```

---

### Scenario 3: Database Corruption

**Impact**: Data integrity issues
**Probability**: Low
**Detection**: Application errors, data validation failures

**Response**:
1. Isolate affected systems
2. Identify corruption scope
3. Point-in-time recovery

**Recovery Steps**:

```bash
# Step 1: Stop writes immediately
kubectl scale deployment mind-api --replicas=0 -n mind-production

# Step 2: Identify last known good state
psql -c "SELECT * FROM events ORDER BY sequence DESC LIMIT 10;"
# Note the last valid sequence number

# Step 3: Perform point-in-time recovery
pgbackrest restore --stanza=mind \
    --target="2025-01-15 14:25:00" \
    --target-action=promote \
    --type=time

# Step 4: Rebuild projections from events
curl -X POST "http://localhost:8000/v1/admin/events/replay" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -d '{"from_sequence": 0, "projections": ["all"]}'

# Step 5: Validate data integrity
./scripts/dr/validate-data-integrity.sh

# Step 6: Resume service
kubectl scale deployment mind-api --replicas=5 -n mind-production
```

---

### Scenario 4: Security Breach / Ransomware

**Impact**: Complete system compromise
**Probability**: Low
**Detection**: SIEM alerts, IDS, anomaly detection

**Response**:
1. Isolate all systems immediately
2. Engage security incident response team
3. Restore from known-clean backup

**Recovery Steps**:

```bash
# IMMEDIATE: Network isolation
# Step 1: Isolate namespace
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: emergency-isolate
  namespace: mind-production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
EOF

# Step 2: Revoke all credentials
./scripts/security/rotate-all-credentials.sh

# Step 3: Create clean environment
./scripts/dr/create-clean-environment.sh --namespace mind-recovery

# Step 4: Restore from verified clean backup
# Use backup from BEFORE the breach detection time
./scripts/dr/restore-from-backup.sh \
    --timestamp "2025-01-14 00:00:00" \
    --verify-integrity \
    --target-namespace mind-recovery

# Step 5: Security audit before go-live
./scripts/security/security-audit.sh --namespace mind-recovery

# Step 6: Cutover to clean environment
kubectl delete namespace mind-production
kubectl create namespace mind-production
# ... restore verified workloads
```

---

### Scenario 5: Cascading Service Failure

**Impact**: Multiple dependent services failing
**Probability**: Medium
**Detection**: Distributed tracing, error rate spikes

**Response**:
1. Enable circuit breakers
2. Isolate failing components
3. Graceful degradation

**Recovery Steps**:

```bash
# Step 1: Enable degraded mode
kubectl set env deployment/mind-api DEGRADED_MODE=true -n mind-production

# Step 2: Scale down non-critical components
kubectl scale deployment mind-worker --replicas=0 -n mind-production

# Step 3: Identify root cause via tracing
# Open Grafana → Tempo → Error traces

# Step 4: Address root cause
# (depends on specific failure)

# Step 5: Gradually restore services
kubectl scale deployment mind-worker --replicas=3 -n mind-production
kubectl set env deployment/mind-api DEGRADED_MODE=false -n mind-production
```

---

## DR Infrastructure

### Multi-Region Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              Route53 (Global)                │
                    │         Health-checked DNS Routing           │
                    └─────────────────┬───────────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              │                                               │
              ▼                                               ▼
    ┌─────────────────────┐                     ┌─────────────────────┐
    │   Primary Region    │                     │  DR Region (Warm)   │
    │    (us-east-1)      │                     │    (us-west-2)      │
    ├─────────────────────┤                     ├─────────────────────┤
    │ ┌─────────────────┐ │   Cross-Region      │ ┌─────────────────┐ │
    │ │   PostgreSQL    │ │───Replication───────│▶│   PostgreSQL    │ │
    │ │   (Primary)     │ │                     │ │   (Standby)     │ │
    │ └─────────────────┘ │                     │ └─────────────────┘ │
    │ ┌─────────────────┐ │                     │ ┌─────────────────┐ │
    │ │      NATS       │ │───Mirror Stream─────│▶│      NATS       │ │
    │ │   (Primary)     │ │                     │ │   (Mirror)      │ │
    │ └─────────────────┘ │                     │ └─────────────────┘ │
    │ ┌─────────────────┐ │                     │ ┌─────────────────┐ │
    │ │   FalkorDB      │ │───S3 Replication────│▶│   FalkorDB      │ │
    │ └─────────────────┘ │                     │ │   (from backup) │ │
    │ ┌─────────────────┐ │                     │ └─────────────────┘ │
    │ │     Qdrant      │ │───S3 Replication────│▶│     Qdrant      │ │
    │ └─────────────────┘ │                     │ │   (from backup) │ │
    │                     │                     │ └─────────────────┘ │
    └─────────────────────┘                     └─────────────────────┘
```

### S3 Cross-Region Replication

```bash
# Verify replication status
aws s3api head-object \
    --bucket mind-backups-dr \
    --key postgres/latest/backup.tar.gz \
    --query 'ReplicationStatus'

# Expected: "COMPLETED"
```

---

## Communication Plan

### Escalation Matrix

| Severity | Response Time | Notification | Escalation |
|----------|---------------|--------------|------------|
| SEV1 (Outage) | 5 min | PagerDuty + Slack | VP Eng within 15 min |
| SEV2 (Degraded) | 15 min | PagerDuty + Slack | Eng Manager within 30 min |
| SEV3 (Potential) | 1 hour | Slack | Team Lead within 2 hours |

### Status Page Updates

```bash
# Update status page (Statuspage.io)
./scripts/status/update-status.sh \
    --component "Mind API" \
    --status "major_outage" \
    --message "Investigating service disruption"

# Automated updates every 30 min during incident
```

---

## DR Testing Schedule

| Test Type | Frequency | Last Test | Next Test |
|-----------|-----------|-----------|-----------|
| Backup Restore | Monthly | 2025-01-01 | 2025-02-01 |
| Component Failover | Quarterly | 2024-12-15 | 2025-03-15 |
| Full Region Failover | Annually | 2024-10-01 | 2025-10-01 |
| Tabletop Exercise | Semi-Annual | 2024-11-15 | 2025-05-15 |

### Test Documentation

All DR test results are documented in:
- Confluence: Platform/DR/Test Results
- GitHub: docs/dr-test-results/

---

## Appendix

### A. Emergency Contacts

| Role | Contact Method |
|------|----------------|
| On-Call Engineer | PagerDuty |
| Platform Lead | PagerDuty escalation |
| VP Engineering | Phone tree |
| Security Team | #security-incident Slack |

### B. External Dependencies

| Service | Impact if Unavailable | Fallback |
|---------|----------------------|----------|
| OpenAI API | No new embeddings | Cached embeddings |
| AWS S3 | No backups | Local NFS |
| Cloudflare | No CDN/WAF | Direct ALB access |

### C. Runbook Cross-References

- [Backup and Recovery](./backup-recovery.md)
- [Database Operations](./database-operations.md)
- [Incident Response](./incident-response.md)
- [Scaling](./scaling.md)
