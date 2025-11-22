# Multi-stage Dockerfile for production
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -e .

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY main.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port (Cloud Run uses PORT env var, default 8080)
# We expose 8080 as default, but the app will use PORT env var
EXPOSE 8080

# Health check (using Python's http.client instead of curl)
# Note: Cloud Run doesn't use HEALTHCHECK, but we keep it for local Docker testing
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import os, http.client; port = int(os.getenv('PORT', '8080')); conn = http.client.HTTPConnection('localhost', port); conn.request('GET', '/health'); r = conn.getresponse(); exit(0 if r.status == 200 else 1)"

# Run application
# Cloud Run sets PORT environment variable (default: 8080)
# Use PORT if set, otherwise default to 8080 for Cloud Run compatibility
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

