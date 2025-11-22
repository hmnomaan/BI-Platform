# BI Platform - End-to-End Guide

Complete guide for building, deploying, and using the BI Platform from start to finish.

## Table of Contents

1. [Overview](#overview)
2. [Complete Setup Process](#complete-setup-process)
3. [Running the Application](#running-the-application)
4. [Using the Dashboard](#using-the-dashboard)
5. [Using the API Engine](#using-the-api-engine)
6. [Integration Examples](#integration-examples)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

## Overview

The BI Platform is a comprehensive solution for:
- **Data Visualization**: Interactive dashboards with multiple chart types
- **API Integration**: Unified interface for third-party services
- **Business Intelligence**: Connect to various data sources and create insights

## Complete Setup Process

### Step 1: Prerequisites Check

```bash
# Check Python version (3.8+ required)
python --version

# Check pip
pip --version

# Check Git (optional)
git --version
```

### Step 2: Clone and Navigate

```bash
git clone <repository-url>
cd bi-platform
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 4: Install Dependencies

#### Option A: Automated Setup (Recommended)

```bash
python setup_and_run.py
```

This will ask if you want to install database drivers. You can skip them if you only use CSV/Excel files.

#### Option A2: Quick Install Without Database (Windows)

If you encounter `psycopg2-binary` build errors on Windows:

```bash
# Windows
install_without_db.bat

# Linux/Mac
chmod +x install_without_db.sh
./install_without_db.sh
```

Or manually:
```bash
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
# Skip: pip install -r requirements/database.txt
```

This will:
- Install all dependencies
- Create sample data
- Set up directory structure
- Optionally start the dashboard

#### Option B: Manual Installation

```bash
# Install base dependencies
pip install -r requirements/base.txt

# Install API Engine dependencies
pip install -r requirements/api.txt

# Install BI Dashboard dependencies
pip install -r requirements/bi.txt

# Install development dependencies (optional)
pip install -r requirements/dev.txt
```

#### Option C: Using Makefile

```bash
make install-all  # Install all dependencies
make setup        # Full setup (install + sample data)
```

### Step 5: Configure Environment

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your settings:
   ```env
   ENVIRONMENT=dev
   SENDGRID_API_KEY=your_key_here
   AWS_ACCESS_KEY_ID=your_key_here
   # ... add other API keys as needed
   ```

   **Note**: For basic dashboard usage, API keys are optional. You only need them if using the API Engine features.

3. **Or edit configuration files directly**:
   - `configs/dev/api_config.yaml` - API Engine settings
   - `configs/dev/bi_config.yaml` - BI Dashboard settings

### Step 6: Create Sample Data

```bash
python scripts/create_sample_data.py
```

This creates:
- `data/sales_data.csv` - Sales data (365 rows)
- `data/employee_data.csv` - Employee data (50 rows)
- `data/time_series_data.csv` - Time series data (1000 rows)

### Step 7: Verify Installation

```bash
# Test imports
python -c "from bi_dashboard import app; print('✓ Dashboard OK')"
python -c "from api_engine import APIEngine; print('✓ API Engine OK')"

# Or run validation script
python scripts/validate_deployment.py
```

## Running the Application

### Running BI Dashboard

#### Method 1: Using Run Script (Recommended)

```bash
python run_app.py
```

#### Method 2: Direct Module

```bash
python -m bi_dashboard.app
```

#### Method 3: Using Makefile

```bash
make run
# or
make run-dashboard
```

#### Method 4: After Package Installation

```bash
bi-dashboard
```

**Access**: Open your browser to **http://127.0.0.1:8050**

### Running API Engine

#### Method 1: Direct Module

```bash
python -m api_engine.http_service
```

#### Method 2: Using Makefile

```bash
make run-api
```

#### Method 3: After Package Installation

```bash
bi-api-server
```

**Access**: API available at **http://localhost:8000**

### Running Both Services

Run in separate terminals:

```bash
# Terminal 1 - Dashboard
python run_app.py

# Terminal 2 - API Engine
python -m api_engine.http_service
```

### Running with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Using the Dashboard

### 1. Access the Dashboard

Open your browser and navigate to: **http://127.0.0.1:8050**

### 2. Upload Data

#### Option A: Upload File

1. Click "Drag and Drop or Select Files"
2. Select a CSV or Excel file
3. Data will be automatically loaded and previewed

#### Option B: Use Sample Data

If you ran `create_sample_data.py`, you can upload:
- `data/sales_data.csv`
- `data/employee_data.csv`
- `data/time_series_data.csv`

### 3. Create Charts

1. **Select Chart Type**:
   - Line Chart - For time series data
   - Bar Chart - For categorical comparisons
   - Pie Chart - For distributions
   - Table - For raw data display

2. **Configure Chart**:
   - **X-Axis Column**: Select the column for X-axis (or Names for Pie)
   - **Y-Axis Column**: Select the column for Y-axis (or Values for Pie)

3. **Create Chart**: Click "Create Chart" button

4. **View Results**: Chart appears in the Charts Display section

### 4. Example Workflows

#### Example 1: Sales Trend Analysis

1. Upload `data/sales_data.csv`
2. Select Chart Type: **Line Chart**
3. X-Axis: **date**
4. Y-Axis: **sales**
5. Click "Create Chart"

Result: Line chart showing sales trend over time

#### Example 2: Regional Comparison

1. Use `sales_data.csv`
2. Select Chart Type: **Bar Chart**
3. X-Axis: **region**
4. Y-Axis: **revenue**
5. Click "Create Chart"

Result: Bar chart comparing revenue by region

#### Example 3: Product Distribution

1. Use `sales_data.csv`
2. Select Chart Type: **Pie Chart**
3. Names: **product**
4. Values: **quantity**
5. Click "Create Chart"

Result: Pie chart showing product distribution

#### Example 4: Employee Data Table

1. Upload `data/employee_data.csv`
2. Select Chart Type: **Table**
3. Click "Create Chart"

Result: Interactive data table with all employee information

## Using the API Engine

### Python API Usage

```python
from api_engine.core.api_engine import APIEngine
from pathlib import Path

# Initialize the engine
engine = APIEngine()

# Send an email
result = engine.send_email(
    to="recipient@example.com",
    subject="Hello from BI Platform",
    content="<h1>Hello World</h1>"
)
print(f"Email sent: {result['message_id']}")

# Upload a file
url = engine.upload_file(
    Path("document.pdf"),
    bucket="documents"
)
print(f"File uploaded: {url}")

# Create an e-signature envelope
envelope_id = engine.create_envelope(
    document=Path("contract.pdf"),
    signers=[
        {"email": "signer@example.com", "name": "John Doe"}
    ]
)
print(f"Envelope created: {envelope_id}")
```

### REST API Usage

#### Send Email

```bash
curl -X POST "http://localhost:8000/api/v1/email/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Hello",
    "content": "<h1>Hello World</h1>"
  }'
```

#### Upload File

```bash
curl -X POST "http://localhost:8000/api/v1/storage/upload" \
  -F "file=@document.pdf" \
  -F "bucket=documents"
```

#### Health Check

```bash
curl http://localhost:8000/health
```

### Configuration

API Engine reads configuration from:
1. Environment variables (`.env` file)
2. `configs/{environment}/api_config.yaml`

Priority: Environment variables > Config files

## Integration Examples

### Flask Integration

```python
from flask import Flask, render_template
from bi_dashboard.core.data_connector import DataSourceManager

app = Flask(__name__)
data_manager = DataSourceManager()

@app.route('/data')
def get_data():
    df = data_manager.read_file(Path("data/sales_data.csv"), "csv")
    return df.to_json(orient='records')
```

See `examples/flask_integration.py` for complete example.

### Django Integration

```python
from django.http import JsonResponse
from bi_dashboard.core.data_connector import DataSourceManager

def get_chart_data(request):
    manager = DataSourceManager()
    df = manager.read_file(Path("data/sales_data.csv"), "csv")
    return JsonResponse(df.to_dict(orient='records'), safe=False)
```

See `examples/django_integration.py` for complete example.

### Business Workflow

```python
from api_engine.core.api_engine import APIEngine
from bi_dashboard.core.data_connector import DataSourceManager

# Initialize
api_engine = APIEngine()
data_manager = DataSourceManager()

# Load data
df = data_manager.read_file(Path("data/sales_data.csv"), "csv")

# Process data
summary = df.groupby('region')['revenue'].sum()

# Send report via email
report_html = summary.to_html()
api_engine.send_email(
    to="manager@example.com",
    subject="Sales Report",
    content=report_html
)
```

See `examples/business_workflow.py` for complete example.

## Production Deployment

### Option 1: Docker (Recommended)

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Gunicorn (Python WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Run dashboard
gunicorn -w 4 -b 0.0.0.0:8050 "bi_dashboard.app:app.server"

# Run API engine (uses Uvicorn)
uvicorn api_engine.http_service:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 3: Systemd Service (Linux)

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

### Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed cloud deployment instructions:
- AWS (EC2, ECS, Elastic Beanstalk)
- Azure (App Service, Container Instances)
- Google Cloud (Compute Engine, Cloud Run)

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process
# Linux/Mac:
lsof -i :8050
# Windows:
netstat -ano | findstr :8050

# Kill process or change port
# Edit run_app.py and change port number
```

#### 2. Module Not Found

**Error**: `ModuleNotFoundError: No module named 'bi_dashboard'`

**Solution**:
```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 3. File Upload Not Working

**Error**: File upload fails or data not loading

**Solution**:
- Ensure file is CSV or Excel format
- Check file encoding (UTF-8 recommended)
- Verify file size (large files may timeout)
- Check browser console for errors

#### 4. Charts Not Displaying

**Error**: Charts don't render

**Solution**:
- Check browser console for JavaScript errors
- Verify data columns exist
- Ensure numeric columns for Y-axis
- Check Plotly version compatibility

#### 5. API Engine Not Working

**Error**: API calls fail

**Solution**:
- Verify API keys in `.env` or config files
- Check provider configuration
- Review logs: `logs/bi_platform.log`
- Test with health endpoint: `curl http://localhost:8000/health`

### Getting Help

1. **Check Logs**:
   ```bash
   tail -f logs/bi_platform.log
   ```

2. **Run Diagnostics**:
   ```bash
   python scripts/validate_deployment.py
   ```

3. **Review Documentation**:
   - `README.md` - Overview
   - `BUILD.md` - Build instructions
   - `DEPLOYMENT.md` - Deployment guide
   - `QUICKSTART.md` - Quick start
   - `docs/` - Detailed documentation

4. **Check Examples**:
   - `examples/api_engine_usage.py`
   - `examples/bi_dashboard_usage.py`
   - `examples/business_workflow.py`

## Next Steps

After successful setup:

1. **Explore Features**:
   - Try different chart types
   - Upload your own data
   - Test API endpoints

2. **Configure Providers**:
   - Set up API keys for email, storage, etc.
   - Test provider integrations

3. **Connect Data Sources**:
   - Connect to databases
   - Set up REST API connections
   - Configure file uploads

4. **Customize**:
   - Modify dashboard layout
   - Add custom chart types
   - Extend API Engine with new providers

5. **Deploy**:
   - Set up production environment
   - Configure monitoring
   - Set up backups

## Additional Resources

- **Architecture**: See `ANALYSIS.md`
- **API Reference**: See `docs/API_REFERENCE.md`
- **Integration Guide**: See `docs/INTEGRATION_GUIDE.md`
- **User Guides**: See `docs/user_guides/`

---

**Congratulations!** You've successfully set up and deployed the BI Platform. Start exploring and building amazing dashboards!

