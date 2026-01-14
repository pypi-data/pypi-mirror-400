# Multi-stage build for Mem-Brain MCP Server

# Builder stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies directly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "fastmcp>=2.0.0,<3.0.0" \
        "httpx>=0.25.0" \
        "pydantic>=2.0.0" \
        "pydantic-settings>=2.0.0" \
        "uvicorn[standard]>=0.27.0"

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Set PYTHONPATH so Python can find the modules
ENV PYTHONPATH=/app/src

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8100/health', timeout=5)" || exit 1

# Run application
CMD ["python", "-m", "mem_brain_mcp"]

