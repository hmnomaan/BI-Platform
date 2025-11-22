# BI Platform Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/ requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt && \
    pip install --no-cache-dir -r requirements/bi.txt && \
    pip install --no-cache-dir -r requirements/api.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Expose ports
# 8050 for BI Dashboard
# 8000 for API Engine
EXPOSE 8050 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod

# Default command (can be overridden)
CMD ["python", "run_app.py"]

