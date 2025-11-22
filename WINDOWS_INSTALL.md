# Windows Installation Guide

Special instructions for installing the BI Platform on Windows.

## Common Issues

### Issue: psycopg2-binary Build Error

**Error**: `ERROR: Failed to build 'psycopg2-binary'`

**Solution**: Database drivers are now optional. The platform works without them if you only use CSV/Excel files.

### Issue: pyyaml or pandas Build Error

**Error**: `ERROR: Failed to build 'pyyaml'` or `ERROR: Failed to build 'pandas'`

**Solution**: This usually happens with Python 3.12+. Try:

1. **Upgrade pip and setuptools first**:
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Install with newer versions**:
   ```bash
   pip install pyyaml>=6.0.1 pandas>=2.0.0
   ```

3. **Or use minimal requirements**:
   ```bash
   pip install -r requirements/base-minimal.txt
   ```

### Issue: psycopg2-binary Build Error

#### Option 1: Skip Database Drivers (Recommended for Quick Start)

The platform works fine without database drivers if you're only using:
- CSV/Excel file uploads
- REST API data sources
- Sample data files

Just skip the database installation:

```bash
# Install without database drivers
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
```

#### Option 2: Install Database Drivers

If you need PostgreSQL connectivity:

**For Python 3.9+ on Windows:**

```bash
pip install psycopg2-binary
```

**For Python 3.8 or if the above fails:**

1. **Install Visual C++ Build Tools**:
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++" workload

2. **Then try again**:
   ```bash
   pip install psycopg2-binary
   ```

**Alternative: Use psycopg2 (requires PostgreSQL client libraries)**

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Install PostgreSQL (or just the client libraries)
3. Add PostgreSQL bin directory to PATH
4. Install:
   ```bash
   pip install psycopg2
   ```

**Alternative: Use SQLite (No Installation Needed)**

SQLite is included with Python. Just use SQLite in your configuration:

```python
# In your code, use SQLite instead
from sqlalchemy import create_engine
engine = create_engine('sqlite:///data.db')
```

## Installation Steps for Windows

### Step 1: Prerequisites

1. **Python 3.8+**: Download from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation
   - Verify: `python --version`

2. **Git** (optional): Download from https://git-scm.com/download/win

### Step 2: Install Dependencies

#### Quick Install (Without Database)

```bash
# Open PowerShell or Command Prompt
cd bi-platform

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies (without database drivers)
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
```

#### Full Install (With Database)

```bash
# Install base dependencies
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt

# Try to install database drivers (optional)
pip install -r requirements/database.txt
```

If database installation fails, you can continue without it.

### Step 3: Setup

```bash
# Create sample data
python scripts/create_sample_data.py

# Create logs directory
mkdir logs
```

### Step 4: Run

```bash
# Run the dashboard
python run_app.py
```

## Using the Setup Script

The setup script now handles database dependencies gracefully:

```bash
python setup_and_run.py
```

It will:
1. Install base dependencies
2. Ask if you want to install database drivers (optional)
3. Create sample data
4. Optionally start the dashboard

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8050
netstat -ano | findstr :8050

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Permission Errors

Run PowerShell or Command Prompt as Administrator.

### Module Not Found

```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements/base.txt
```

### pip Install Fails

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install dependencies
pip install -r requirements/base.txt
```

## Alternative: Use Docker

If you have Docker Desktop installed:

```bash
# Build and run with Docker
docker-compose up -d
```

This avoids Windows-specific build issues.

## Database-Free Usage

The BI Platform works perfectly without database drivers:

1. **File Upload**: Upload CSV/Excel files directly
2. **REST APIs**: Connect to REST API data sources
3. **Sample Data**: Use pre-generated sample data files

Database drivers are only needed if you want to:
- Connect to PostgreSQL databases
- Connect to MySQL databases
- Use database connections in the dashboard

## Next Steps

Once installed:
1. Run `python run_app.py`
2. Open http://127.0.0.1:8050 in your browser
3. Upload a CSV file or use sample data
4. Create charts!

For more help, see:
- [BUILD.md](BUILD.md) - Complete build guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [END_TO_END_GUIDE.md](END_TO_END_GUIDE.md) - Full guide

