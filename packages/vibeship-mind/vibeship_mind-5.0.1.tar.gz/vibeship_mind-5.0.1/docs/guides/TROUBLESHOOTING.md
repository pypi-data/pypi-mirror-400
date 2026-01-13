# Troubleshooting Guide

> Solutions for common issues with Mind v5

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Connection Issues](#connection-issues)
3. [API Errors](#api-errors)
4. [Memory Issues](#memory-issues)
5. [Decision Tracking Issues](#decision-tracking-issues)
6. [Performance Issues](#performance-issues)
7. [Docker Issues](#docker-issues)
8. [Workflow Issues](#workflow-issues)
9. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Check Everything at Once

```bash
# Full system check
curl http://localhost:8000/ready | python -m json.tool

# Expected output shows all components
```

### Component Health Commands

```bash
# API health
curl http://localhost:8000/health

# Database
docker exec -it mind-postgres psql -U mind -c "SELECT 1"

# NATS
curl http://localhost:8222/healthz

# FalkorDB
docker exec -it mind-falkordb redis-cli PING

# Temporal
curl http://localhost:8088/api/v1/cluster-info
```

### Check Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f mind-api
docker-compose logs -f postgres
docker-compose logs -f nats
```

---

## Connection Issues

### Database Connection Failed

**Symptoms:**
- API returns 500 errors
- `/ready` shows `database: disconnected`
- Logs show: `Connection refused` or `could not connect to server`

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   docker-compose ps postgres
   # Should show "Up" status
   ```

2. **Check connection settings:**
   ```bash
   # Verify DATABASE_URL in .env
   echo $DATABASE_URL

   # Test connection
   psql $DATABASE_URL -c "SELECT 1"
   ```

3. **Check PostgreSQL logs:**
   ```bash
   docker-compose logs postgres | tail -50
   ```

4. **Restart PostgreSQL:**
   ```bash
   docker-compose restart postgres
   sleep 5
   docker-compose restart mind-api
   ```

5. **Check pgvector extension:**
   ```bash
   psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector"
   ```

### NATS Connection Failed

**Symptoms:**
- Events not being published
- `/ready` shows `nats: disconnected`
- Logs show: `NATS connection error`

**Solutions:**

1. **Check NATS is running:**
   ```bash
   docker-compose ps nats
   curl http://localhost:8222/healthz
   ```

2. **Check NATS URL:**
   ```bash
   # Should be nats://nats:4222 in Docker, nats://localhost:4222 locally
   echo $NATS_URL
   ```

3. **Check NATS logs:**
   ```bash
   docker-compose logs nats | tail -50
   ```

4. **Restart NATS:**
   ```bash
   docker-compose restart nats
   ```

**Note:** NATS is optional for basic operations. The API works without it but events won't be published.

### FalkorDB Connection Failed

**Symptoms:**
- Causal endpoints return errors
- `/ready` shows `falkordb: error`

**Solutions:**

1. **Check FalkorDB is running:**
   ```bash
   docker-compose ps falkordb
   docker exec -it mind-falkordb redis-cli PING
   ```

2. **Check connection settings:**
   ```bash
   echo $FALKORDB_HOST
   echo $FALKORDB_PORT
   ```

3. **Restart FalkorDB:**
   ```bash
   docker-compose restart falkordb
   ```

### Temporal Connection Failed

**Symptoms:**
- Workflows not running
- `/ready` shows `temporal: error`

**Solutions:**

1. **Check Temporal is running:**
   ```bash
   docker-compose ps temporal
   ```

2. **Wait for startup:**
   Temporal can take 30-60 seconds to fully initialize.
   ```bash
   sleep 60
   curl http://localhost:8000/ready
   ```

3. **Check Temporal logs:**
   ```bash
   docker-compose logs temporal | tail -100
   ```

---

## API Errors

### 401 Unauthorized

**Cause:** Authentication required but no token provided.

**Solution:**
```bash
# Check if auth is required
grep REQUIRE_AUTH .env

# If auth is enabled, get a token and include it
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/v1/memories/...
```

### 403 Forbidden

**Cause:** Token valid but insufficient permissions.

**Solution:**
- Check the token's scopes
- Ensure the scope matches the endpoint requirements
- Request a token with appropriate scopes

### 422 Unprocessable Entity

**Cause:** Invalid request data.

**Common issues:**

1. **Invalid UUID:**
   ```json
   // Wrong
   {"user_id": "not-a-uuid"}

   // Correct
   {"user_id": "550e8400-e29b-41d4-a716-446655440000"}
   ```

2. **Invalid temporal_level:**
   ```json
   // Wrong
   {"temporal_level": "identity"}

   // Correct
   {"temporal_level": 4}
   ```

3. **Invalid quality:**
   ```json
   // Wrong
   {"quality": 2.0}

   // Correct (must be -1.0 to 1.0)
   {"quality": 0.85}
   ```

4. **Missing required field:**
   ```json
   // Wrong - missing content
   {"user_id": "..."}

   // Correct
   {"user_id": "...", "content": "Memory content", "temporal_level": 3}
   ```

### 429 Too Many Requests

**Cause:** Rate limit exceeded.

**Solution:**
```bash
# Check rate limit headers
curl -I http://localhost:8000/v1/memories/

# Wait for reset
# X-RateLimit-Reset header shows when

# Or disable rate limiting in development
# RATE_LIMIT_ENABLED=false in .env
```

### 500 Internal Server Error

**Cause:** Server-side error.

**Steps:**
1. Check API logs:
   ```bash
   docker-compose logs mind-api | tail -100
   ```

2. Check for database issues:
   ```bash
   curl http://localhost:8000/ready
   ```

3. Restart the API:
   ```bash
   docker-compose restart mind-api
   ```

---

## Memory Issues

### Retrieval Returns Empty Results

**Symptoms:**
- `POST /v1/memories/retrieve` returns `{"memories": []}`
- Even though memories exist

**Solutions:**

1. **Check memories exist for user:**
   ```bash
   # Create a test memory first
   curl -X POST http://localhost:8000/v1/memories/ \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "YOUR_USER_ID",
       "content": "Test memory content",
       "temporal_level": 4
     }'
   ```

2. **Check query matches content:**
   - Vector search requires OpenAI API key for embeddings
   - Without embeddings, only keyword matching works
   - Try exact word matches from memory content

3. **Enable embeddings:**
   ```bash
   # Add to .env
   OPENAI_API_KEY=sk-your-key-here

   # Restart API
   docker-compose restart mind-api
   ```

4. **Lower salience threshold:**
   ```json
   {
     "user_id": "...",
     "query": "test",
     "limit": 10,
     "min_salience": 0.0
   }
   ```

### Memory Creation Fails

**Symptoms:**
- 500 error on `POST /v1/memories/`

**Solutions:**

1. **Check required fields:**
   ```json
   {
     "user_id": "valid-uuid",
     "content": "non-empty string",
     "temporal_level": 1  // must be 1, 2, 3, or 4
   }
   ```

2. **Check user_id format:**
   Must be valid UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

3. **Check database connection:**
   ```bash
   curl http://localhost:8000/ready
   ```

### Salience Not Updating

**Symptoms:**
- Recording outcomes doesn't change memory salience

**Solutions:**

1. **Verify outcome was recorded:**
   ```bash
   curl http://localhost:8000/v1/decisions/{trace_id}
   # Check if outcome exists
   ```

2. **Check NATS is connected:**
   Salience updates happen via events
   ```bash
   curl http://localhost:8000/ready
   # nats should be "connected"
   ```

3. **Check workers are running:**
   ```bash
   docker-compose ps mind-worker
   ```

---

## Decision Tracking Issues

### Trace ID Not Found

**Symptoms:**
- `GET /v1/decisions/{trace_id}` returns 404

**Cause:** Trace ID doesn't exist or expired.

**Solutions:**
1. Verify you're using the correct trace_id from the track response
2. Check if the decision was actually created
3. Trace IDs are case-sensitive

### Outcome Recording Fails

**Symptoms:**
- 404 or 422 error on `POST /v1/decisions/outcome`

**Solutions:**

1. **Check trace_id exists:**
   ```bash
   curl http://localhost:8000/v1/decisions/{trace_id}
   ```

2. **Check quality range:**
   ```json
   // Must be -1.0 to 1.0
   {"quality": 0.85}  // Correct
   {"quality": 2.0}   // Wrong
   ```

3. **Check signal value:**
   ```json
   // Must be one of: "positive", "neutral", "negative"
   {"signal": "positive"}  // Correct
   {"signal": "good"}      // Wrong
   ```

---

## Performance Issues

### Slow Retrieval

**Symptoms:**
- Retrieval takes >500ms
- Timeouts on large queries

**Solutions:**

1. **Check vector index:**
   ```sql
   -- Connect to PostgreSQL
   -- Check if index exists
   SELECT indexname FROM pg_indexes WHERE tablename = 'memories';

   -- Create if missing
   CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops);
   ```

2. **Reduce limit:**
   ```json
   {"query": "...", "limit": 5}  // Instead of 50
   ```

3. **Add filters:**
   ```json
   {
     "query": "...",
     "temporal_levels": [3, 4],
     "min_salience": 0.5
   }
   ```

4. **Check PostgreSQL resources:**
   ```bash
   docker stats mind-postgres
   ```

### High Memory Usage

**Symptoms:**
- Container using excessive memory
- OOM errors

**Solutions:**

1. **Limit embedding cache:**
   Embeddings are cached in memory. Restart to clear.
   ```bash
   docker-compose restart mind-api
   ```

2. **Increase container limits:**
   ```yaml
   # docker-compose.yaml
   services:
     mind-api:
       deploy:
         resources:
           limits:
             memory: 2G
   ```

### High CPU Usage

**Symptoms:**
- CPU consistently high
- Slow responses

**Solutions:**

1. **Check for runaway queries:**
   ```bash
   docker exec mind-postgres psql -U mind -c "SELECT * FROM pg_stat_activity WHERE state = 'active'"
   ```

2. **Scale workers:**
   ```bash
   docker-compose scale mind-api=3
   ```

---

## Docker Issues

### Containers Not Starting

```bash
# Check status
docker-compose ps

# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache

# Full restart
docker-compose down
docker-compose up -d
```

### Port Already in Use

```bash
# Find what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Kill the process or use different port
API_PORT=8001 docker-compose up -d
```

### Out of Disk Space

```bash
# Check disk usage
docker system df

# Clean up
docker system prune -a

# Remove unused volumes
docker volume prune
```

---

## Workflow Issues

### Workflows Not Running

**Symptoms:**
- No workflows visible in Temporal UI (http://localhost:8088)
- Scheduled tasks not executing

**Solutions:**

1. **Check worker is running:**
   ```bash
   docker-compose ps mind-worker
   ```

2. **Check Temporal connection:**
   ```bash
   curl http://localhost:8000/ready
   # temporal should be "connected"
   ```

3. **Start worker manually:**
   ```bash
   python -m mind.workers.worker
   ```

4. **Check Temporal UI:**
   Visit http://localhost:8088 and look for the `gardener` task queue

### Workflow Failing

1. **Check Temporal UI:**
   - Go to http://localhost:8088
   - Find the workflow
   - Check the event history for errors

2. **Check worker logs:**
   ```bash
   docker-compose logs mind-worker | tail -100
   ```

---

## Getting Help

### Collect Debug Information

When reporting issues, collect:

```bash
# System info
echo "=== System ===" > debug.txt
uname -a >> debug.txt

# Docker info
echo "=== Docker ===" >> debug.txt
docker-compose ps >> debug.txt

# Health status
echo "=== Health ===" >> debug.txt
curl http://localhost:8000/ready >> debug.txt

# Recent logs
echo "=== Logs ===" >> debug.txt
docker-compose logs --tail=100 >> debug.txt
```

### Log Levels

Increase logging for debugging:

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart
docker-compose restart mind-api
```

### Contact

- **GitHub Issues**: Open an issue with debug information
- **Logs**: Include relevant log excerpts
- **Reproducible Steps**: Provide exact steps to reproduce the issue

---

## Quick Reference

### Restart Everything

```bash
docker-compose down
docker-compose up -d
```

### Reset Database

```bash
docker-compose down -v  # Removes volumes
docker-compose up -d
```

### View All Logs

```bash
docker-compose logs -f --tail=100
```

### Check All Ports

```bash
docker-compose ps --format "{{.Name}}: {{.Ports}}"
```
