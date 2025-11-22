# Quick Run Guide

## You're Already in Virtual Environment! ✓

If you see `(.venv)` in your prompt, you're already in the virtual environment.

## Running the API

### Step 1: Make sure dependencies are installed

```bash
# Check if dependencies are installed
python -c "import yaml, fastapi; print('✓ Dependencies installed')"

# If that fails, install dependencies:
pip install -r requirements/base.txt
pip install -r requirements/api.txt
```

### Step 2: Run the API

```bash
# Option 1: Using the run script (Recommended)
python run_api.py

# Option 2: Direct module (if package is installed)
python -m api_engine.http_service

# Option 3: Using Makefile
make run-api
```

### Step 3: Test the API

Once running, open in browser:
- **API Root**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or test with curl:
```bash
curl http://localhost:8000/health
```

## Running the Dashboard

```bash
python run_app.py
```

Access at: http://127.0.0.1:8050

## Troubleshooting

### If "No module named 'yaml'" error:
```bash
pip install pyyaml
```

### If "No module named 'api_engine'" error:
```bash
# Make sure you're in the project directory
cd /mnt/d/XU/projects-xlab/bi-platform/bi-platform

# Install package in development mode
pip install -e .
```

### If dependencies are missing:
```bash
# Install all dependencies
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
```

