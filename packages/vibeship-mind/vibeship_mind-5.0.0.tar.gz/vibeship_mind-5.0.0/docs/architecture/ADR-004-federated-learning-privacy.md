# ADR-004: Federated Learning with Differential Privacy

## Status
Accepted

## Context
Users can benefit from patterns discovered across the user base, but privacy must be preserved. No individual user's data should be identifiable in shared patterns.

## Decision
Implement federated pattern learning with differential privacy:

1. **Pattern Extraction:** Identify successful decision patterns from outcomes
2. **Local Aggregation:** Aggregate patterns per user locally
3. **Privacy Sanitization:** Apply differential privacy (epsilon = 0.1)
4. **Global Aggregation:** Combine sanitized patterns across users
5. **Pattern Application:** Apply global patterns to new decisions

**Privacy Guarantees:**
- Minimum 100 samples before pattern sharing
- Minimum 10 distinct users per pattern
- Laplace noise with epsilon = 0.1
- No PII in pattern content (abstracted categories)

## Consequences

### Positive
- Collective intelligence benefits all users
- Strong privacy guarantees (epsilon-differential privacy)
- Improved decisions for new users
- Measurable pattern effectiveness

### Negative
- Reduced pattern precision due to noise
- Computational overhead for sanitization
- Need for careful category abstraction

### Mitigations
- High sample thresholds for quality
- Category mapping removes PII
- Regular privacy audits
