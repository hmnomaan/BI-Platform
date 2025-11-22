# BI Platform - Deployment Guide

Complete guide for deploying the BI Platform in various environments.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Best Practices](#production-best-practices)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Scaling](#scaling)

## Deployment Overview

The BI Platform consists of two main services:

1. **BI Dashboard** - Web-based dashboard (Port 8050)
2. **API Engine** - REST API service (Port 8000)

Both services can be deployed independently or together.

## Local Development

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd bi-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/bi.txt
pip install -r requirements/api.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Create sample data
python scripts/create_sample_data.py

# 6. Run services
python run_app.py  # Dashboard
python -m api_engine.http_service  # API Engine
```

## Docker Deployment

### Quick Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Configuration

Edit `docker-compose.yml` to customize:

- Ports
- Environment variables
- Volume mounts
- Resource limits

### Production Docker Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  bi-dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8050:8050"
    environment:
      - ENVIRONMENT=prod
    env_file:
      - .env.prod
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  api-engine:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
    env_file:
      - .env.prod
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2 Instance

1. **Launch EC2 Instance**:
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium or larger
   - Security Group: Open ports 8050, 8000, 22

2. **Install Dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv git
   ```

3. **Deploy Application**:
   ```bash
   git clone <repository-url>
   cd bi-platform
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements/base.txt
   pip install -r requirements/bi.txt
   pip install -r requirements/api.txt
   ```

4. **Run with Systemd**:
   Create `/etc/systemd/system/bi-platform.service`:
   ```ini
   [Unit]
   Description=BI Platform
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/bi-platform
   Environment="PATH=/home/ubuntu/bi-platform/venv/bin"
   ExecStart=/home/ubuntu/bi-platform/venv/bin/python run_app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start Service**:
   ```bash
   sudo systemctl enable bi-platform
   sudo systemctl start bi-platform
   ```

#### Option 2: ECS (Elastic Container Service)

1. **Build and Push Docker Image**:
   ```bash
   docker build -t bi-platform .
   docker tag bi-platform:latest <account-id>.dkr.ecr.<region>.amazonaws.com/bi-platform:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/bi-platform:latest
   ```

2. **Create ECS Task Definition**:
   - Use the pushed image
   - Configure ports 8050 and 8000
   - Set environment variables

3. **Create ECS Service**:
   - Select task definition
   - Configure load balancer
   - Set desired count

#### Option 3: Elastic Beanstalk

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**:
   ```bash
   eb init -p python-3.9 bi-platform
   ```

3. **Create Environment**:
   ```bash
   eb create bi-platform-env
   ```

4. **Deploy**:
   ```bash
   eb deploy
   ```

### Azure Deployment

#### Option 1: Azure App Service

1. **Create App Service**:
   ```bash
   az webapp create --resource-group myResourceGroup \
     --plan myAppServicePlan --name bi-platform --runtime "PYTHON|3.9"
   ```

2. **Configure App Settings**:
   ```bash
   az webapp config appsettings set --resource-group myResourceGroup \
     --name bi-platform --settings ENVIRONMENT=prod
   ```

3. **Deploy**:
   ```bash
   az webapp deployment source config-local-git \
     --name bi-platform --resource-group myResourceGroup
   git remote add azure <deployment-url>
   git push azure main
   ```

#### Option 2: Azure Container Instances

1. **Build and Push to ACR**:
   ```bash
   az acr build --registry <registry-name> --image bi-platform .
   ```

2. **Create Container Instance**:
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name bi-platform \
     --image <registry-name>.azurecr.io/bi-platform:latest \
     --dns-name-label bi-platform \
     --ports 8050 8000
   ```

### Google Cloud Platform

#### Option 1: Compute Engine

Similar to AWS EC2 deployment.

#### Option 2: Cloud Run

1. **Build and Push to GCR**:
   ```bash
   gcloud builds submit --tag gcr.io/<project-id>/bi-platform
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy bi-platform \
     --image gcr.io/<project-id>/bi-platform \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Production Best Practices

### Security

1. **Environment Variables**:
   - Never commit `.env` files
   - Use secret management (AWS Secrets Manager, Azure Key Vault)
   - Rotate API keys regularly

2. **HTTPS**:
   - Use reverse proxy (Nginx, Apache) with SSL certificates
   - Configure Let's Encrypt for free SSL

3. **Authentication**:
   - Implement user authentication
   - Use API keys for API access
   - Enable rate limiting

4. **Network Security**:
   - Use firewall rules
   - Restrict database access
   - Use VPN for internal services

### Performance

1. **Caching**:
   - Enable Redis for session caching
   - Cache frequently accessed data
   - Use CDN for static assets

2. **Database Optimization**:
   - Use connection pooling
   - Index frequently queried columns
   - Regular database maintenance

3. **Resource Limits**:
   - Set appropriate memory limits
   - Configure CPU limits
   - Monitor resource usage

### Monitoring

1. **Application Monitoring**:
   - Use logging (structured logs)
   - Set up error tracking (Sentry)
   - Monitor response times

2. **Infrastructure Monitoring**:
   - CPU and memory usage
   - Disk I/O
   - Network traffic

3. **Health Checks**:
   - Implement `/health` endpoints
   - Set up automated alerts
   - Monitor uptime

### Backup and Recovery

1. **Data Backups**:
   - Regular database backups
   - Backup configuration files
   - Version control for code

2. **Disaster Recovery**:
   - Document recovery procedures
   - Test backup restoration
   - Maintain off-site backups

## Monitoring and Maintenance

### Logging

Configure logging in `configs/prod/bi_config.yaml`:

```yaml
logging:
  level: INFO
  file: logs/bi_platform.log
  max_size: 10MB
  backup_count: 5
```

### Health Checks

```bash
# Dashboard health
curl http://localhost:8050

# API health
curl http://localhost:8000/health
```

### Performance Monitoring

Use tools like:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for log aggregation
- **New Relic** or **Datadog** for APM

### Regular Maintenance

1. **Update Dependencies**:
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

2. **Database Maintenance**:
   - Regular VACUUM (PostgreSQL)
   - Index optimization
   - Query performance analysis

3. **Security Updates**:
   - Keep OS updated
   - Update Python packages
   - Review security advisories

## Scaling

### Horizontal Scaling

1. **Load Balancer**:
   - Use Nginx or HAProxy
   - Configure multiple instances
   - Session affinity if needed

2. **Multiple Instances**:
   ```bash
   # Run multiple dashboard instances
   gunicorn -w 4 -b 0.0.0.0:8050 "bi_dashboard.app:app.server"
   ```

3. **Database Scaling**:
   - Read replicas for read-heavy workloads
   - Connection pooling
   - Query optimization

### Vertical Scaling

1. **Increase Resources**:
   - More CPU cores
   - More RAM
   - Faster storage (SSD)

2. **Optimize Code**:
   - Profile application
   - Optimize slow queries
   - Cache expensive operations

### Auto-Scaling

Configure auto-scaling based on:
- CPU utilization
- Memory usage
- Request rate
- Response time

Example (AWS Auto Scaling):
```yaml
min_size: 2
max_size: 10
target_cpu_utilization: 70
```

## Troubleshooting

### Common Deployment Issues

1. **Port Conflicts**:
   - Check if ports are already in use
   - Change ports in configuration

2. **Permission Errors**:
   - Check file permissions
   - Ensure user has necessary access

3. **Import Errors**:
   - Verify PYTHONPATH
   - Check virtual environment activation
   - Reinstall dependencies

4. **Database Connection**:
   - Verify database is running
   - Check network connectivity
   - Verify credentials

### Getting Help

- Check logs: `logs/bi_platform.log`
- Review documentation: `docs/`
- Run diagnostics: `python scripts/validate_deployment.py`

---

For more information, see:
- `BUILD.md` - Build instructions
- `README.md` - Project overview
- `docs/deployment/` - Detailed deployment guides

