# Service Level Objectives (SLOs)

## Overview

This document defines the Service Level Objectives for Mind v5 production systems.
SLOs are measured over a 30-day rolling window unless otherwise specified.

## API Availability

### SLO: 99.9% Availability

**Definition:** The API is considered available when:
- Health endpoint returns 200 OK
- Response time < 30 seconds
- Error rate < 5%

**Measurement:**
```promql
# Availability calculation
1 - (
  sum(rate(mind_http_requests_total{status=~"5.."}[30d])) /
  sum(rate(mind_http_requests_total[30d]))
)
```

**Error Budget:** 43.2 minutes/month of downtime allowed

| Target | Monthly Budget | Alert Threshold |
|--------|---------------|-----------------|
| 99.9%  | 43.2 min      | 99.5% (7-day)   |

## API Latency

### SLO: P99 Latency < 500ms

**Definition:** 99% of requests complete within 500ms

**Measurement:**
```promql
histogram_quantile(0.99,
  sum(rate(mind_http_request_duration_seconds_bucket[30d])) by (le)
)
```

**Targets by Endpoint:**

| Endpoint | P50 | P95 | P99 |
|----------|-----|-----|-----|
| GET /health | 5ms | 20ms | 50ms |
| GET /memories | 50ms | 200ms | 500ms |
| POST /decisions/track | 100ms | 300ms | 500ms |
| POST /decisions/{id}/outcome | 50ms | 150ms | 300ms |

## Memory Retrieval Quality

### SLO: Retrieval Relevance > 0.7

**Definition:** Retrieved memories have average relevance score > 0.7

**Measurement:**
```promql
avg(mind_memory_retrieval_relevance) > 0.7
```

**Quality Metrics:**

| Metric | Target | Alert |
|--------|--------|-------|
| Avg Relevance | > 0.7 | < 0.6 |
| Empty Results | < 5% | > 10% |
| Stale Results | < 2% | > 5% |

## Decision Outcome Tracking

### SLO: 95% Decisions Have Outcomes

**Definition:** 95% of tracked decisions receive outcome feedback within 7 days

**Measurement:**
```promql
sum(mind_outcomes_observed_total) /
sum(mind_decisions_tracked_total{age>"7d"}) > 0.95
```

## Event Processing

### SLO: Event Processing Lag < 30s

**Definition:** Events are processed within 30 seconds of publication

**Measurement:**
```promql
max(mind_event_processing_lag_seconds) < 30
```

**Targets:**

| Metric | Target | Critical |
|--------|--------|----------|
| Avg Lag | < 5s | > 30s |
| Max Lag | < 30s | > 60s |
| Failed Events | < 0.1% | > 1% |

## Database Performance

### SLO: Query Latency P99 < 100ms

**Measurement:**
```promql
histogram_quantile(0.99,
  sum(rate(mind_db_query_duration_seconds_bucket[30d])) by (le, query_type)
)
```

**Targets by Query Type:**

| Query Type | P50 | P95 | P99 |
|------------|-----|-----|-----|
| Simple Read | 5ms | 20ms | 50ms |
| Vector Search | 20ms | 50ms | 100ms |
| Graph Traverse | 10ms | 30ms | 80ms |
| Write | 10ms | 30ms | 100ms |

## Embedding Service

### SLO: Cache Hit Rate > 80%

**Definition:** 80% of embedding requests served from cache

**Measurement:**
```promql
sum(rate(mind_embedding_cache_hits_total[30d])) /
sum(rate(mind_embedding_requests_total[30d])) > 0.8
```

## Federated Learning

### SLO: Pattern Freshness < 24h

**Definition:** Federated patterns updated within 24 hours of new data

**Privacy Compliance:** 100% of patterns pass differential privacy validation

## Alerting Thresholds

### Critical (Page immediately):
- Availability < 99%
- P99 Latency > 2s
- Error rate > 10%
- Event lag > 5 minutes

### Warning (Slack notification):
- Availability < 99.5%
- P99 Latency > 1s
- Error rate > 5%
- Cache hit rate < 70%

## Error Budget Policy

1. **> 50% budget remaining:** Normal development velocity
2. **25-50% budget remaining:** Increased testing, careful deployments
3. **< 25% budget remaining:** Focus on reliability, freeze non-critical changes
4. **Budget exhausted:** All hands on reliability, rollback risky changes

## Review Cadence

- **Weekly:** SLO status review in team standup
- **Monthly:** Error budget review with stakeholders
- **Quarterly:** SLO target review and adjustment
