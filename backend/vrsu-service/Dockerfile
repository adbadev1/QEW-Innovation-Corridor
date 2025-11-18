# QEW vRSU Service - Docker Container
# =====================================
# Lightweight Python container for GCP Cloud Run deployment
#
# Build: docker build -t qew-vrsu-service .
# Run:   docker run -p 8080:8080 qew-vrsu-service
# Deploy: gcloud run deploy vrsu-service --source .

# Use official Python runtime (slim for smaller image)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expose port (Cloud Run will override this)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/')"

# Run FastAPI with uvicorn
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1
