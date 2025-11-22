# BI Platform - Complete Build Guide

This guide provides comprehensive instructions for building, running, and deploying the BI Platform from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Building the Project](#building-the-project)
5. [Running the Application](#running-the-application)
6. [Docker Deployment](#docker-deployment)
7. [Production Deployment](#production-deployment)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.8+** (3.9 or 3.10 recommended)
- **pip** (Python package manager)
- **Git** (for version control)

### Optional Software

- **Docker** and **Docker Compose** (for containerized deployment)
- **PostgreSQL** (for database connections)
- **Make** (for using Makefile commands)

### System Requirements

- **RAM**: Minimum 2GB, Recommended 4GB+
- **Disk Space**: Minimum 1GB free space
- **Network**: Internet connection for package installation

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd bi-platform

# Run automated setup
python setup_and_run.py
```

This will:
- Install all dependencies
- Create sample data files
- Set up directory structure
- Optionally start the dashboard

### Option 2: Using Makefile

```bash
# Full setup
make setup

# Run the dashboard
make run
```

### Option 3: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/bi.txt
pip install -r requirements/api.txt

# 2. Create directories
mkdir -p logs data

# 3. Create sample data
python scripts/create_sample_data.py

# 4. Run the application
python run_app.py
```

## Detailed Installation

### Step 1: Verify Python Version

```bash
python --version
# Should show Python 3.8 or higher
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

#### Base Installation (Minimum)

```bash
pip install -r requirements/base.txt
```

This installs:
- Core dependencies (pandas, plotly, dash)
- API Engine base (requests, boto3)
- Common utilities

#### Full Installation

```bash
# Install all components
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
pip install -r requirements/dev.txt
```

Or use the Makefile:

```bash
make install-all
```

### Step 4: Configure Environment

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your API keys and configuration:
   ```env
   ENVIRONMENT=dev
   SENDGRID_API_KEY=your_key_here
   AWS_ACCESS_KEY_ID=your_key_here
   # ... etc
   ```

3. **Or edit configuration files directly:**
   - `configs/dev/api_config.yaml` - API Engine settings
   - `configs/dev/bi_config.yaml` - BI Dashboard settings

### Step 5: Create Sample Data

```bash
python scripts/create_sample_data.py
```

This creates:
- `data/sales_data.csv` - Sales data with dates, regions, products
- `data/employee_data.csv` - Employee information
- `data/time_series_data.csv` - Time series sensor data

## Building the Project

### Install as a Package

```bash
# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Build Distribution Packages

```bash
# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel

# Both will be in dist/ directory
```

## Running the Application

### BI Dashboard

#### Method 1: Using Run Script
```bash
python run_app.py
```

#### Method 2: Direct Module
```bash
python -m bi_dashboard.app
```

#### Method 3: Using Entry Point (after pip install)
```bash
bi-dashboard
```

#### Method 4: Using Makefile
```bash
make run
# or
make run-dashboard
```

Access the dashboard at: **http://127.0.0.1:8050**

### API Engine

#### Method 1: Direct Module
```bash
python -m api_engine.http_service
```

#### Method 2: Using Entry Point (after pip install)
```bash
bi-api-server
```

#### Method 3: Using Makefile
```bash
make run-api
```

API will be available at: **http://localhost:8000**

### Running Both Services

You can run both services simultaneously in separate terminals:

```bash
# Terminal 1
python run_app.py

# Terminal 2
python -m api_engine.http_service
```

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+

### Build Docker Images

```bash
# Build images
docker-compose build

# Or using Makefile
make docker-build
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Or using Makefile
make docker-up

# View logs
docker-compose logs -f

# Or using Makefile
make docker-logs
```

### Access Services

- **BI Dashboard**: http://localhost:8050
- **API Engine**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### Stop Services

```bash
docker-compose down

# Or using Makefile
make docker-down
```

### Docker Commands

```bash
# Build specific service
docker-compose build bi-dashboard

# View logs for specific service
docker-compose logs -f bi-dashboard

# Execute command in container
docker-compose exec bi-dashboard bash

# Restart service
docker-compose restart bi-dashboard
```

## Production Deployment

### Using Gunicorn (Recommended for Production)

```bash
# Install Gunicorn
pip install gunicorn

# Run BI Dashboard with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8050 "bi_dashboard.app:app.server"

# Run API Engine with Uvicorn (already included)
uvicorn api_engine.http_service:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables for Production

Set these in your production environment:

```bash
export ENVIRONMENT=prod
export DB_HOST=your_production_db_host
export DB_PASSWORD=your_secure_password
# ... etc
```

### Reverse Proxy Setup (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Service (Linux)

Create `/etc/systemd/system/bi-platform.service`:

```ini
[Unit]
Description=BI Platform Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/bi-platform
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:8050 "bi_dashboard.app:app.server"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable bi-platform
sudo systemctl start bi-platform
```

## Verification

### Check Installation

```bash
# Test Python imports
python -c "from bi_dashboard import app; print('✓ Dashboard OK')"
python -c "from api_engine import APIEngine; print('✓ API Engine OK')"
```

### Test Data Loading

```python
from bi_dashboard.core.data_connector import DataSourceManager
from pathlib import Path

manager = DataSourceManager()
df = manager.read_file(Path("data/sales_data.csv"), "csv")
print(f"Loaded {len(df)} rows")
```

### Run Tests

```bash
# All tests
pytest tests/

# Or using Makefile
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration
```

### Health Checks

```bash
# Dashboard health (when running)
curl http://localhost:8050

# API Engine health
curl http://localhost:8000/health
```

## Windows-Specific Notes

If you're on Windows and encounter issues with `psycopg2-binary`, see [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for detailed Windows installation instructions.

**Quick fix**: Database drivers are optional. You can skip them if you only use CSV/Excel files:

```bash
# Install without database drivers
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port
# On Linux/Mac:
lsof -i :8050
# On Windows:
netstat -ano | findstr :8050

# Kill process or change port in run_app.py
```

#### 2. Module Not Found

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements/base.txt
pip install -r requirements/bi.txt
pip install -r requirements/api.txt
```

#### 3. Import Errors

**Error**: `ImportError` or `No module named 'bi_dashboard'`

**Solution**:
```bash
# Install package in development mode
pip install -e .

# Or add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 4. File Upload Not Working

**Error**: File upload fails or data not loading

**Solution**:
- Ensure file is CSV or Excel format
- Check file size (large files may timeout)
- Verify file encoding (UTF-8 recommended)
- Check browser console for errors

#### 5. Database Connection Fails

**Error**: `OperationalError` or connection timeout

**Solution**:
- Verify database is running
- Check credentials in config or `.env`
- Install appropriate driver:
  ```bash
  pip install psycopg2-binary  # For PostgreSQL
  pip install pymysql          # For MySQL
  ```

#### 6. Docker Build Fails

**Error**: `ERROR: Failed to build 'pyyaml'` or similar package build errors

**Solution** (Python 3.12+ compatibility):
```bash
# Upgrade pip and build tools first
python -m pip install --upgrade pip setuptools wheel

# Try installing with updated versions
pip install pyyaml>=6.0.1 pandas>=2.0.0

# Or use minimal requirements
pip install -r requirements/base-minimal.txt
```

#### 8. Docker Build Fails

**Error**: Build errors or missing dependencies

**Solution**:
```bash
# Clean build
docker-compose down
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t bi-platform .
```

#### 7. Charts Not Displaying

**Error**: Charts don't render or show errors

**Solution**:
- Check browser console for JavaScript errors
- Verify data columns exist in uploaded data
- Ensure numeric columns for Y-axis
- Check Plotly version compatibility

### Getting Help

1. **Check Logs**:
   ```bash
   # Application logs
   tail -f logs/bi_platform.log

   # Docker logs
   docker-compose logs -f
   ```

2. **Review Documentation**:
   - `README.md` - Overview and features
   - `QUICKSTART.md` - Quick start guide
   - `docs/` - Detailed documentation

3. **Run Diagnostics**:
   ```bash
   python scripts/validate_deployment.py
   ```

## Next Steps

After successful build and deployment:

1. **Explore Examples**: Check `examples/` directory for usage patterns
2. **Read API Documentation**: See `docs/API_REFERENCE.md`
3. **Configure Providers**: Set up API keys in `.env` or config files
4. **Customize Dashboard**: Modify `bi_dashboard/app.py` for your needs
5. **Add Data Sources**: Connect to your databases or APIs
6. **Extend Functionality**: Add new providers or chart types

## Additional Resources

- **Architecture**: See `ANALYSIS.md` for system architecture
- **API Reference**: See `docs/API_REFERENCE.md`
- **Integration Guide**: See `docs/INTEGRATION_GUIDE.md`
- **Deployment Guide**: See `docs/deployment/` directory

---

**Need Help?** Open an issue on GitHub or check the documentation in the `docs/` directory.

