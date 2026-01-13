#!/bin/bash
# Mind v5 API Examples
# Usage: bash scripts/examples.sh

API="http://localhost:8080"
USER_ID="550e8400-e29b-41d4-a716-446655440000"

echo "=== Mind v5 API Examples ==="
echo ""

# 1. Health Check
echo "1. Health Check"
curl -s "$API/health" | jq .
echo ""

# 2. Create a Memory
echo "2. Create Memory"
MEMORY_RESPONSE=$(curl -s -X POST "$API/v1/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "content": "User prefers TypeScript over JavaScript for new projects",
    "content_type": "preference",
    "temporal_level": 4,
    "base_salience": 0.9
  }')
echo "$MEMORY_RESPONSE" | jq .
MEMORY_ID=$(echo "$MEMORY_RESPONSE" | jq -r '.memory_id')
echo ""

# 3. List Memories
echo "3. List Memories"
curl -s "$API/v1/memories?user_id=$USER_ID&limit=5" | jq .
echo ""

# 4. Search Memories
echo "4. Search Memories"
curl -s -X POST "$API/v1/memories/search" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "query": "programming language preferences",
    "limit": 3
  }' | jq .
echo ""

# 5. Track a Decision
echo "5. Track Decision"
DECISION_RESPONSE=$(curl -s -X POST "$API/v1/decisions/track" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'",
    "query": "What language should we use for this new microservice?",
    "context": {"project_type": "api", "team_size": 3},
    "decision_made": "Recommended TypeScript based on user preference",
    "confidence": 0.92,
    "memory_ids": ["'$MEMORY_ID'"]
  }')
echo "$DECISION_RESPONSE" | jq .
TRACE_ID=$(echo "$DECISION_RESPONSE" | jq -r '.trace_id')
echo ""

# 6. Record Outcome
echo "6. Record Outcome"
curl -s -X POST "$API/v1/decisions/$TRACE_ID/outcome" \
  -H "Content-Type: application/json" \
  -d '{
    "outcome_value": 1.0,
    "feedback": "User was happy with TypeScript recommendation"
  }' | jq .
echo ""

echo "=== Done ==="
