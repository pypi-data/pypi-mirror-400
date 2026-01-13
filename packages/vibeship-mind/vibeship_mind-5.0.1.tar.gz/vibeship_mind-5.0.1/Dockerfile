# Mind v5 API Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy all source files first (required for install)
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Install Python dependencies (including ml and vector optional deps for consumers)
RUN pip install --no-cache-dir ".[ml,vector]"

# Create non-root user
RUN useradd -m -u 1000 mind && chown -R mind:mind /app
USER mind

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the API
CMD ["python", "-m", "mind.cli", "serve", "--host", "0.0.0.0", "--port", "8080"]
