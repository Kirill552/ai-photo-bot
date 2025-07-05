FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (build context = ./src/worker)
COPY . ./worker/

# Create directories
RUN mkdir -p /var/log/worker
RUN mkdir -p /tmp/worker

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from worker.health import check_health; check_health()" || exit 1

# Run the YC MQ worker (not Celery)
CMD ["python", "-m", "worker.main"] 