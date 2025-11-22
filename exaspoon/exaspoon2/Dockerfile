# Use Python 3.12 slim as base image
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY spoon-core/ ./spoon-core/

# Install dependencies using uv
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install -e . && \
    cd spoon-core && \
    uv pip install -e . && \
    cd ..

# Copy application code
COPY . .

# Make the venv the default environment
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5556

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5556/api/status || exit 1

# Default command (will be overridden by docker-compose)
CMD ["uv", "run", "app.py"]