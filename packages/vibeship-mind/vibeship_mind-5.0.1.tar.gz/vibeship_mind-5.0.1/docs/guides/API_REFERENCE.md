# API Reference

> Complete documentation for all Mind v5 API endpoints

**Base URL:** `http://localhost:8000`

**Content-Type:** All requests use `application/json`

**Authentication:** JWT Bearer token (when enabled)

---

## Table of Contents

1. [Health Endpoints](#health-endpoints)
2. [Memory Endpoints](#memory-endpoints)
3. [Decision Endpoints](#decision-endpoints)
4. [Causal Endpoints](#causal-endpoints)
5. [Consent Endpoints](#consent-endpoints)
6. [Admin Endpoints](#admin-endpoints)
7. [Metrics](#metrics)
8. [Error Handling](#error-handling)

---

## Health Endpoints

### GET /health

Basic health check. Returns OK if API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "5.0.0"
}
```

### GET /ready

Readiness check with all component statuses.

**Response:**
```json
{
  "ready": true,
  "database": "connected",
  "nats": "connected",
  "falkordb": "connected",
  "temporal": "connected",
  "qdrant": "not_configured"
}
```

### GET /health/detailed

Full component health details.

**Response:**
```json
{
  "status": "healthy",
  "version": "5.0.0",
  "components": {
    "database": {"status": "healthy", "type": "postgresql"},
    "nats": {"status": "healthy", "type": "jetstream"},
    "falkordb": {"status": "healthy", "type": "graph"},
    "temporal": {"status": "healthy", "type": "workflow"},
    "qdrant": {"status": "not_configured", "type": "vector"}
  }
}
```

### GET /anomalies

Run anomaly detection on memory patterns.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_window_hours` | int | 24 | Hours to look back (1-168) |
| `user_id` | UUID | null | Filter to specific user |

**Response:**
```json
{
  "anomalies": [
    {
      "type": "creation_spike",
      "severity": "high",
      "user_id": "550e8400...",
      "message": "Memory creation rate is 5.0x normal",
      "details": {"current_count": 100, "prior_count": 20},
      "detected_at": "2025-01-15T10:30:00Z"
    }
  ],
  "checked_at": "2025-01-15T10:30:00Z",
  "time_window_hours": 24,
  "user_count_checked": 10,
  "memory_count_checked": 150,
  "summary": {
    "total": 1,
    "critical": 0,
    "high": 1,
    "medium": 0,
    "low": 0
  }
}
```

---

## Memory Endpoints

### POST /v1/memories/

Create a new memory.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "User prefers TypeScript over JavaScript",
  "temporal_level": 4,
  "base_salience": 0.8,
  "valid_until": null,
  "tags": ["preferences", "languages"],
  "metadata": {"source": "conversation"}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | Yes | Owner of this memory |
| `content` | string | Yes | The memory content |
| `temporal_level` | int | Yes | 1-4, persistence level |
| `base_salience` | float | No | 0.0-1.0, default 0.5 |
| `valid_until` | datetime | No | Expiration time |
| `tags` | string[] | No | Categorization tags |
| `metadata` | object | No | Additional metadata |

**Response (200 OK):**
```json
{
  "memory_id": "abc123-def456-...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "User prefers TypeScript over JavaScript",
  "temporal_level": 4,
  "base_salience": 0.8,
  "outcome_adjustment": 0.0,
  "created_at": "2025-01-15T10:30:00Z",
  "valid_until": null
}
```

### GET /v1/memories/{memory_id}

Retrieve a specific memory by ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `memory_id` | UUID | Memory identifier |

**Response (200 OK):**
```json
{
  "memory_id": "abc123-def456-...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "User prefers TypeScript over JavaScript",
  "temporal_level": 4,
  "base_salience": 0.8,
  "outcome_adjustment": 0.05,
  "created_at": "2025-01-15T10:30:00Z",
  "valid_until": null,
  "tags": ["preferences", "languages"],
  "metadata": {"source": "conversation"}
}
```

### POST /v1/memories/retrieve

Retrieve relevant memories for a query.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "What programming language does the user prefer?",
  "limit": 10,
  "min_salience": 0.3,
  "temporal_levels": [3, 4],
  "include_expired": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | Yes | User to search for |
| `query` | string | Yes | Search query |
| `limit` | int | No | Max results (default 10) |
| `min_salience` | float | No | Minimum effective salience |
| `temporal_levels` | int[] | No | Filter by levels |
| `include_expired` | bool | No | Include expired memories |

**Response (200 OK):**
```json
{
  "memories": [
    {
      "memory_id": "abc123...",
      "content": "User prefers TypeScript over JavaScript",
      "temporal_level": 4,
      "base_salience": 0.8,
      "outcome_adjustment": 0.05,
      "effective_salience": 0.85,
      "score": 0.92,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "retrieval_time_ms": 45,
  "total_candidates": 25,
  "sources": {
    "vector": 10,
    "keyword": 5,
    "salience": 8,
    "causal": 2
  }
}
```

---

## Decision Endpoints

### POST /v1/decisions/track

Track a decision with its context.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "query": "How should I structure my API?",
  "context": "User asked about REST API design",
  "memory_ids": ["abc123...", "def456..."],
  "confidence": 0.85
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | Yes | User making decision |
| `session_id` | UUID | Yes | Current session |
| `query` | string | Yes | Decision query |
| `context` | string | No | Additional context |
| `memory_ids` | UUID[] | No | Explicitly used memories |
| `confidence` | float | No | Decision confidence 0-1 |

**Response (200 OK):**
```json
{
  "trace_id": "tr-789abc...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "query": "How should I structure my API?",
  "retrieved_memories": ["abc123...", "def456..."],
  "confidence": 0.85,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### POST /v1/decisions/outcome

Record the outcome of a decision.

**Request Body:**
```json
{
  "trace_id": "tr-789abc...",
  "quality": 0.85,
  "signal": "positive",
  "feedback": "User was satisfied with the recommendation"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trace_id` | string | Yes | Decision trace ID |
| `quality` | float | Yes | -1.0 to 1.0 |
| `signal` | string | Yes | "positive", "neutral", "negative" |
| `feedback` | string | No | Optional feedback text |

**Response (200 OK):**
```json
{
  "trace_id": "tr-789abc...",
  "quality": 0.85,
  "signal": "positive",
  "memories_adjusted": 3,
  "adjustments": [
    {"memory_id": "abc123...", "delta": 0.04},
    {"memory_id": "def456...", "delta": 0.03}
  ],
  "recorded_at": "2025-01-15T10:35:00Z"
}
```

### GET /v1/decisions/{trace_id}

Get details of a tracked decision.

**Response (200 OK):**
```json
{
  "trace_id": "tr-789abc...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "660e8400-e29b-41d4-a716-446655440001",
  "query": "How should I structure my API?",
  "context": "User asked about REST API design",
  "retrieved_memories": ["abc123...", "def456..."],
  "confidence": 0.85,
  "outcome": {
    "quality": 0.85,
    "signal": "positive",
    "feedback": "User was satisfied",
    "recorded_at": "2025-01-15T10:35:00Z"
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

### POST /v1/decisions/context

Get decision context (memories and predictions).

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "What framework should I use?",
  "limit": 10
}
```

**Response (200 OK):**
```json
{
  "memories": [...],
  "predicted_quality": 0.75,
  "similar_decisions": 5,
  "recommendations": [
    "Consider user's preference for TypeScript",
    "User has experience with React"
  ]
}
```

---

## Causal Endpoints

### GET /v1/causal/attribution/{trace_id}

Get causal attribution for a decision.

**Response (200 OK):**
```json
{
  "trace_id": "tr-789abc...",
  "attributions": [
    {
      "memory_id": "abc123...",
      "contribution": 0.45,
      "retrieval_rank": 1,
      "content_preview": "User prefers TypeScript..."
    },
    {
      "memory_id": "def456...",
      "contribution": 0.35,
      "retrieval_rank": 2,
      "content_preview": "User building web app..."
    }
  ],
  "outcome_quality": 0.85,
  "learning_applied": true
}
```

### POST /v1/causal/predict

Predict outcome for a potential decision.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "How to implement authentication?",
  "memory_ids": ["abc123...", "def456..."]
}
```

**Response (200 OK):**
```json
{
  "predicted_quality": 0.72,
  "confidence": 0.65,
  "similar_decisions_count": 8,
  "quality_distribution": {
    "positive": 6,
    "neutral": 1,
    "negative": 1
  }
}
```

### POST /v1/causal/counterfactual

Analyze what-if scenarios.

**Request Body:**
```json
{
  "trace_id": "tr-789abc...",
  "removed_memory_ids": ["abc123..."],
  "added_memory_ids": []
}
```

**Response (200 OK):**
```json
{
  "original_outcome": 0.85,
  "counterfactual_outcome": 0.45,
  "impact": -0.40,
  "removed_memories": [
    {"memory_id": "abc123...", "contribution": 0.45}
  ],
  "conclusion": "Removing this memory would likely decrease outcome quality"
}
```

### GET /v1/causal/memory/{memory_id}/success-rate

Get success rate for a specific memory.

**Response (200 OK):**
```json
{
  "memory_id": "abc123...",
  "total_uses": 25,
  "positive_outcomes": 20,
  "neutral_outcomes": 3,
  "negative_outcomes": 2,
  "success_rate": 0.80,
  "average_quality": 0.72
}
```

---

## Consent Endpoints

### POST /v1/consent/grant

Grant user consent.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "consent_type": "federated_learning",
  "expires_at": "2026-01-15T00:00:00Z"
}
```

### POST /v1/consent/revoke

Revoke user consent.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "consent_type": "federated_learning"
}
```

### GET /v1/consent/settings/{user_id}

Get user's consent settings.

### POST /v1/consent/check

Check if user has specific consent.

### GET /v1/consent/has/{user_id}/{consent_type}

Quick consent check.

### GET /v1/consent/audit/{user_id}

Get consent change history.

### GET /v1/consent/expiring

Get consents expiring soon.

---

## Admin Endpoints

All admin endpoints require elevated permissions.

### GET /v1/admin/status

System status overview.

**Response (200 OK):**
```json
{
  "version": "5.0.0",
  "uptime_seconds": 3600,
  "memory_count": 1500,
  "decision_count": 500,
  "active_users": 25,
  "components": {...}
}
```

### GET /v1/admin/dlq/stats

Dead letter queue statistics.

**Response (200 OK):**
```json
{
  "count": 5,
  "oldest": "2025-01-15T09:00:00Z",
  "newest": "2025-01-15T10:00:00Z",
  "by_error_type": {
    "timeout": 2,
    "validation": 3
  }
}
```

### GET /v1/admin/dlq/messages

List DLQ messages.

### GET /v1/admin/dlq/messages/{sequence}

Get specific DLQ message.

### POST /v1/admin/dlq/replay/{sequence}

Replay a single DLQ message.

### POST /v1/admin/dlq/replay-all

Replay all DLQ messages.

### GET /v1/admin/events/info

Event stream information.

### POST /v1/admin/events/replay

Replay events for rebuilding state.

### GET /v1/admin/patterns/effectiveness

Pattern effectiveness metrics.

### GET /v1/admin/scopes/check

Check authorization scopes.

---

## Metrics

### GET /metrics

Prometheus metrics endpoint.

**Key Metrics:**

```
# Memory operations
mind_memory_created_total
mind_memory_retrieved_total
mind_memory_salience_adjusted_total

# Decision tracking
mind_decision_tracked_total
mind_decision_outcome_recorded_total
mind_decision_outcome_quality{signal="positive|neutral|negative"}

# Performance
mind_retrieval_latency_seconds
mind_embedding_latency_seconds
mind_causal_query_latency_seconds

# System
mind_active_users_gauge
mind_memory_count_gauge
mind_decision_count_gauge
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": {
    "code": "MEMORY_NOT_FOUND",
    "message": "Memory with ID abc123 not found",
    "context": {"memory_id": "abc123"}
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (invalid data) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

### Error Codes

| Code | Description |
|------|-------------|
| `MEMORY_NOT_FOUND` | Memory does not exist |
| `DECISION_NOT_FOUND` | Decision trace not found |
| `USER_NOT_FOUND` | User does not exist |
| `INVALID_TEMPORAL_LEVEL` | Level must be 1-4 |
| `INVALID_SALIENCE` | Salience must be 0.0-1.0 |
| `INVALID_QUALITY` | Quality must be -1.0 to 1.0 |
| `CAUSAL_CYCLE` | Circular causal reference |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `DATABASE_ERROR` | Database operation failed |
| `NATS_ERROR` | Event publishing failed |

---

## Rate Limiting

When rate limiting is enabled:

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312800
```

**429 Response:**
```json
{
  "detail": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again in 30 seconds.",
    "retry_after": 30
  }
}
```

---

## Authentication

When authentication is enabled, include JWT token:

```bash
curl -H "Authorization: Bearer eyJhbG..." http://localhost:8000/v1/memories/
```

**Token Structure:**
```json
{
  "sub": "user-uuid",
  "scopes": ["memories:read", "memories:write", "decisions:*"],
  "exp": 1705312800
}
```

**Required Scopes:**
| Endpoint | Required Scope |
|----------|----------------|
| `GET /v1/memories/*` | `memories:read` |
| `POST /v1/memories/` | `memories:write` |
| `POST /v1/memories/retrieve` | `memories:read` |
| `POST /v1/decisions/*` | `decisions:write` |
| `GET /v1/decisions/*` | `decisions:read` |
| `GET /v1/admin/*` | `admin:read` |
| `POST /v1/admin/*` | `admin:write` |
