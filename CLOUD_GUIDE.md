# BI Platform - Cloud Deployment Guide

Complete guide for deploying the BI Platform to cloud platforms.

## Table of Contents

1. [Cloud Overview](#cloud-overview)
2. [AWS Deployment](#aws-deployment)
3. [Azure Deployment](#azure-deployment)
4. [Google Cloud Deployment](#google-cloud-deployment)
5. [Multi-Cloud Strategy](#multi-cloud-strategy)
6. [Cloud Best Practices](#cloud-best-practices)
7. [Cost Optimization](#cost-optimization)

## Cloud Overview

### Why Cloud Deployment?

- **Scalability**: Easily scale up/down based on demand
- **Reliability**: High availability and redundancy
- **Global Reach**: Deploy to multiple regions
- **Managed Services**: Use cloud-native services
- **Cost Efficiency**: Pay only for what you use

### Cloud Service Models

1. **Infrastructure as a Service (IaaS)**: EC2, Azure VM, GCE
2. **Platform as a Service (PaaS)**: Elastic Beanstalk, App Service, Cloud Run
3. **Container as a Service (CaaS)**: ECS, AKS, GKE
4. **Function as a Service (FaaS)**: Lambda, Azure Functions, Cloud Functions

## AWS Deployment

### Option 1: EC2 (Infrastructure)

**Best For**: Full control, custom configurations

#### Step 1: Launch EC2 Instance

```bash
# Create EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --user-data file://user-data.sh
```

#### Step 2: Configure Security Group

```
Inbound Rules:
- SSH (22) - Your IP
- HTTP (80) - 0.0.0.0/0
- HTTPS (443) - 0.0.0.0/0
- Dashboard (8050) - Load Balancer only
- API (8000) - Load Balancer only
```

#### Step 3: Install Dependencies

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Python and dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git

# Clone repository
git clone <repository-url>
cd bi-platform

# Install application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
```

#### Step 4: Configure Systemd Service

```ini
# /etc/systemd/system/bi-platform.service
[Unit]
Description=BI Platform Dashboard
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

#### Step 5: Start Service

```bash
sudo systemctl enable bi-platform
sudo systemctl start bi-platform
```

### Option 2: Elastic Beanstalk (PaaS)

**Best For**: Easy deployment, automatic scaling

#### Step 1: Install EB CLI

```bash
pip install awsebcli
```

#### Step 2: Initialize Application

```bash
eb init -p python-3.9 bi-platform
```

#### Step 3: Create Environment

```bash
eb create bi-platform-env
```

#### Step 4: Deploy

```bash
eb deploy
```

### Option 3: ECS (Container)

**Best For**: Container orchestration, microservices

#### Step 1: Build and Push Image

```bash
# Build Docker image
docker build -t bi-platform .

# Tag for ECR
docker tag bi-platform:latest <account-id>.dkr.ecr.<region>.amazonaws.com/bi-platform:latest

# Push to ECR
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/bi-platform:latest
```

#### Step 2: Create ECS Task Definition

```json
{
  "family": "bi-platform",
  "containerDefinitions": [
    {
      "name": "dashboard",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/bi-platform:latest",
      "portMappings": [
        {
          "containerPort": 8050,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "prod"
        }
      ]
    }
  ]
}
```

#### Step 3: Create ECS Service

```bash
aws ecs create-service \
  --cluster bi-platform-cluster \
  --service-name bi-platform-service \
  --task-definition bi-platform \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...
```

### AWS Services Integration

#### S3 for File Storage

```python
# Configure S3 in configs/prod/api_config.yaml
storage:
  provider: s3
  s3:
    bucket: bi-platform-storage
    region: us-east-1
```

#### RDS for Database

```yaml
# Connect to RDS PostgreSQL
database:
  host: bi-platform-db.xxxxx.rds.amazonaws.com
  port: 5432
  name: bi_platform
```

#### CloudWatch for Monitoring

```python
# Enable CloudWatch logging
import boto3
cloudwatch = boto3.client('clouds')
```

## Azure Deployment

### Option 1: Virtual Machines

**Best For**: Full control, custom configurations

#### Step 1: Create VM

```bash
az vm create \
  --resource-group bi-platform-rg \
  --name bi-platform-vm \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys
```

#### Step 2: Open Ports

```bash
az vm open-port \
  --port 80 \
  --resource-group bi-platform-rg \
  --name bi-platform-vm
```

### Option 2: App Service (PaaS)

**Best For**: Easy deployment, automatic scaling

#### Step 1: Create App Service Plan

```bash
az appservice plan create \
  --name bi-platform-plan \
  --resource-group bi-platform-rg \
  --sku B1 \
  --is-linux
```

#### Step 2: Create Web App

```bash
az webapp create \
  --resource-group bi-platform-rg \
  --plan bi-platform-plan \
  --name bi-platform-app \
  --runtime "PYTHON|3.9"
```

#### Step 3: Deploy

```bash
az webapp deployment source config-local-git \
  --name bi-platform-app \
  --resource-group bi-platform-rg

git remote add azure <deployment-url>
git push azure main
```

### Option 3: Container Instances

**Best For**: Simple container deployment

#### Step 1: Build and Push to ACR

```bash
az acr build --registry <registry-name> --image bi-platform .
```

#### Step 2: Create Container Instance

```bash
az container create \
  --resource-group bi-platform-rg \
  --name bi-platform-container \
  --image <registry-name>.azurecr.io/bi-platform:latest \
  --dns-name-label bi-platform \
  --ports 8050 8000 \
  --environment-variables ENVIRONMENT=prod
```

### Azure Services Integration

#### Blob Storage

```python
# Configure Azure Blob in configs/prod/api_config.yaml
storage:
  provider: azure
  azure:
    connection_string: DefaultEndpointsProtocol=https;AccountName=...
```

#### Azure Database for PostgreSQL

```yaml
database:
  host: bi-platform-db.postgres.database.azure.com
  port: 5432
  name: bi_platform
```

## Google Cloud Deployment

### Option 1: Compute Engine

Similar to AWS EC2 deployment process.

### Option 2: Cloud Run (Serverless)

**Best For**: Serverless container deployment

#### Step 1: Build and Push to GCR

```bash
gcloud builds submit --tag gcr.io/<project-id>/bi-platform
```

#### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy bi-platform \
  --image gcr.io/<project-id>/bi-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8050
```

### Google Cloud Services Integration

#### Cloud Storage

```python
# Configure Cloud Storage
storage:
  provider: gcs
  gcs:
    bucket: bi-platform-storage
```

#### Cloud SQL

```yaml
database:
  host: <instance-ip>
  port: 5432
  name: bi_platform
```

## Multi-Cloud Strategy

### Hybrid Deployment

```
┌─────────────┐      ┌─────────────┐
│   AWS       │      │   Azure     │
│ Dashboard   │◄────►│ API Engine  │
└─────────────┘      └─────────────┘
```

### Benefits

- **Redundancy**: Avoid vendor lock-in
- **Performance**: Deploy closer to users
- **Cost**: Use best pricing from each cloud

## Cloud Best Practices

### 1. Security

- **Use IAM roles**: Don't hardcode credentials
- **Enable encryption**: At rest and in transit
- **Use VPC**: Isolate resources
- **Enable logging**: Monitor all access

### 2. High Availability

- **Multi-region deployment**: Deploy to multiple regions
- **Load balancing**: Distribute traffic
- **Auto-scaling**: Scale based on demand
- **Health checks**: Monitor service health

### 3. Monitoring

- **CloudWatch/Azure Monitor/GCP Monitoring**: Monitor resources
- **Application Insights**: Track application metrics
- **Log aggregation**: Centralized logging
- **Alerting**: Set up alerts for issues

### 4. Backup & Disaster Recovery

- **Regular backups**: Automated backups
- **Multi-region backups**: Store in multiple regions
- **Disaster recovery plan**: Document recovery procedures
- **Test recovery**: Regularly test backup restoration

## Cost Optimization

### Cost Management Strategies

1. **Right-sizing**: Use appropriate instance sizes
2. **Reserved Instances**: Commit to 1-3 year terms (AWS)
3. **Spot Instances**: Use for non-critical workloads
4. **Auto-scaling**: Scale down during low usage
5. **Monitoring**: Track costs closely

### Estimated Costs (AWS Example)

**Small Deployment**:
- EC2 t3.medium: ~$30/month
- RDS db.t3.micro: ~$15/month
- S3 storage: ~$5/month
- **Total**: ~$50/month

**Medium Deployment**:
- EC2 t3.large (2x): ~$120/month
- RDS db.t3.small: ~$50/month
- S3 + CloudWatch: ~$20/month
- **Total**: ~$190/month

### Cost Optimization Tips

1. **Use Spot Instances**: 50-90% savings (AWS)
2. **Schedule Scaling**: Scale down nights/weekends
3. **Optimize Storage**: Use appropriate storage classes
4. **Cache Frequently**: Reduce API calls
5. **Monitor Usage**: Set up billing alerts

## Cloud Architecture Patterns

### Serverless Architecture

```
API Gateway → Lambda → DynamoDB
                ↓
          CloudWatch Logs
```

### Microservices Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Dashboard│  │ API      │  │ Data     │
│ Service  │  │ Service  │  │ Service  │
└──────────┘  └──────────┘  └──────────┘
       ↓           ↓           ↓
┌─────────────────────────────────┐
│      Service Mesh / API GW      │
└─────────────────────────────────┘
```

## Deployment Checklist

### Pre-Deployment

- [ ] Review security settings
- [ ] Configure environment variables
- [ ] Set up database
- [ ] Configure storage buckets
- [ ] Set up monitoring
- [ ] Create backup strategy

### Deployment

- [ ] Build Docker images
- [ ] Push to container registry
- [ ] Deploy to cloud
- [ ] Configure load balancer
- [ ] Set up SSL certificates
- [ ] Configure DNS

### Post-Deployment

- [ ] Verify health checks
- [ ] Test all endpoints
- [ ] Monitor logs
- [ ] Set up alerts
- [ ] Document deployment
- [ ] Train team

## Troubleshooting

### Common Issues

1. **Connection Timeout**: Check security groups/firewalls
2. **High Costs**: Review instance sizes and usage
3. **Performance Issues**: Check instance types and scaling
4. **Database Connection**: Verify VPC and security settings

### Getting Help

- Check cloud provider documentation
- Review application logs
- Use cloud provider support
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for general deployment issues

---

For more information:
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Azure Documentation](https://docs.microsoft.com/azure/)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [DEPLOYMENT.md](DEPLOYMENT.md) for general deployment guide

