# Production Dockerfile for py-flowcheck applications
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PY_FLOWCHECK_ENV=prod
ENV PY_FLOWCHECK_SAMPLE_SIZE=0.1
ENV PY_FLOWCHECK_MODE=log
ENV PY_FLOWCHECK_ENABLE_METRICS=true

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install py-flowcheck
RUN pip install -e .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from py_flowcheck.monitoring import is_healthy; exit(0 if is_healthy() else 1)"

# Default command
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]