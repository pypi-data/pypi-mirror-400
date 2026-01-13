# Mind v5 Grafana Dashboards

Pre-built Grafana dashboards for monitoring Mind v5 decision intelligence system.

## Dashboards

### SLO Overview (`slo-overview.json`)

Service Level Objectives dashboard tracking Mind v5's reliability and quality targets:

**SLO Summary**
- Overall SLO status (healthy/failing)
- Number of SLOs meeting targets
- 30-day rolling window indicators

**Decision Quality SLOs**
- Decision success rate (target: >= 80%)
- Error budget remaining
- Calibration error (target: <= 0.10)
- Trend graphs with SLO threshold lines

**Latency SLOs**
- API p99 latency (target: <= 500ms)
- Memory retrieval relevance p90 (target: >= 70%)
- Embedding cache hit rate (target: >= 80%)
- Latency percentile trends

**Reliability SLOs**
- API availability (target: 99.9%)
- Event processing success (target: 99%)
- Workflow success rate (target: 99%)
- Error rate trends
- Dead letter queue depth

**SLO Definitions**
- Complete reference table of all SLOs
- Error budget policy
- Incident response procedures

### Decision Feedback Loop (`feedback-loop.json`)

Visualizes the complete feedback loop that powers Mind v5's learning:

**Decision Flow Overview**
- Decisions tracked vs outcomes observed
- Rolling success rate gauge
- Confidence calibration error (ECE)
- Outcome quality distribution (positive/negative/neutral)

**Memory Feedback Loop**
- Salience adjustments (increases/decreases) based on outcomes
- Memory retrieval relevance percentiles (p50, p90, p99)

**Pattern Learning**
- Patterns extracted from successful outcomes
- Patterns sanitized for federation (differential privacy)
- Patterns applied to new decisions
- Pattern effectiveness by type
- Privacy budget consumption

**Causal Attribution**
- Causal graph growth (Memory→Decision, Decision→Outcome edges)
- Causal prediction accuracy by type
- Attribution and counterfactual query counts

**Embedding & Cache Performance**
- Embedding cache hit rate
- Embedding generation latency percentiles

## Installation

### Docker Compose

Add to your `docker-compose.yml`:

```yaml
grafana:
  image: grafana/grafana:10.0.0
  ports:
    - "3000:3000"
  volumes:
    - ./deploy/grafana/provisioning:/etc/grafana/provisioning
    - ./deploy/grafana/dashboards:/var/lib/grafana/dashboards
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_USERS_ALLOW_SIGN_UP=false
```

### Kubernetes

1. Create a ConfigMap from the dashboard JSON:

```bash
kubectl create configmap mind-dashboards \
  --from-file=feedback-loop.json=deploy/grafana/dashboards/feedback-loop.json
```

2. Mount in your Grafana deployment and configure the provisioning path.

### Manual Import

1. Open Grafana UI (default: http://localhost:3000)
2. Go to Dashboards → Import
3. Upload `feedback-loop.json`
4. Select your Prometheus datasource
5. Click Import

## Prerequisites

- Prometheus datasource configured in Grafana
- Mind v5 API exposing metrics at `/metrics`
- Prometheus scraping the Mind v5 metrics endpoint

## Metrics Reference

The dashboard uses these Mind v5 metrics:

| Metric | Description |
|--------|-------------|
| `mind_decisions_tracked_total` | Decisions tracked by type |
| `mind_outcomes_observed_total` | Outcomes by quality |
| `mind_decision_success_rate` | Rolling success rate |
| `mind_confidence_calibration_error` | ECE by cohort |
| `mind_salience_adjustments_total` | Salience changes |
| `mind_memory_retrieval_relevance` | Relevance histogram |
| `mind_patterns_extracted_total` | Pattern extraction count |
| `mind_patterns_sanitized_total` | DP-sanitized patterns |
| `mind_patterns_applied_total` | Patterns used in decisions |
| `mind_pattern_effectiveness` | Outcome improvement |
| `mind_privacy_budget_spent` | DP epsilon consumed |
| `mind_causal_edges_created_total` | Graph edge count |
| `mind_causal_prediction_accuracy` | Prediction accuracy |
| `mind_causal_attributions_computed_total` | Attribution queries |
| `mind_counterfactual_queries_total` | What-if queries |
| `mind_embedding_cache_hits_total` | Cache hits |
| `mind_embedding_cache_misses_total` | Cache misses |
| `mind_embedding_latency_seconds` | Embedding latency |

## Customization

Dashboard uses a `$datasource` variable for Prometheus. Override this in Grafana settings if your datasource has a different name.
