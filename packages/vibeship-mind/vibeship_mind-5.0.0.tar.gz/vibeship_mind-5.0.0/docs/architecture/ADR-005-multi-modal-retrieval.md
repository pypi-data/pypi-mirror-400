# ADR-005: Multi-Modal Retrieval with RRF Fusion

## Status
Accepted

## Context
Memory retrieval needs to consider multiple signals:
- Semantic similarity (vector search)
- Causal relationships (graph traversal)
- Keyword matching (full-text search)
- Temporal relevance (recency)
- Outcome history (salience)

## Decision
Implement multi-modal retrieval with Reciprocal Rank Fusion (RRF):

**Retrieval Sources:**
1. **Qdrant:** Vector similarity search on embeddings
2. **FalkorDB:** Graph traversal for causal context
3. **PostgreSQL:** Full-text search and salience ranking

**Fusion Algorithm:**
```
RRF_score(d) = Sum of 1 / (k + rank_i(d))
```
Where k=60 (standard constant) and rank_i is the rank from source i.

**Weighting:**
- Vector: 0.4 (semantic relevance)
- Graph: 0.3 (causal context)
- Salience: 0.2 (proven value)
- Recency: 0.1 (temporal relevance)

## Consequences

### Positive
- Robust retrieval combining multiple signals
- Graceful degradation if one source fails
- Tunable weights for different use cases
- Better recall than single-source

### Negative
- Latency from multiple sources
- Complexity in result merging
- Need for weight tuning

### Mitigations
- Parallel source queries
- Caching frequent queries
- A/B testing for weight optimization
