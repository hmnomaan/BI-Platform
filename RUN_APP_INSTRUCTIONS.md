# Quick Instructions to Run the BI Platform Dashboard

## Step 1: Install Dependencies

Since you're getting a `ModuleNotFoundError: No module named 'dash'`, you need to install the dependencies first.

### Option 1: Install All Required Dependencies (Recommended)

Run these commands in your terminal:

```bash
# Install base dependencies (includes dash, plotly, pandas, etc.)
pip install -r requirements/base.txt

# Install BI Dashboard specific dependencies
pip install -r requirements/bi.txt

# Install API Engine dependencies (optional, but recommended)
pip install -r requirements/api.txt
```

### Option 2: Use the Automated Setup Script

```bash
python setup_and_run.py
```

This will:
- Install all dependencies
- Create sample data
- Optionally start the dashboard

### Option 3: Quick Install (Without Database Drivers)

If you encounter issues with database drivers, you can skip them:

```bash
pip install -r requirements/base.txt
pip install -r requirements/bi.txt
# Skip database.txt if you only use CSV/Excel files
```

## Step 2: Run the Application

Once dependencies are installed, run:

```bash
python run_app.py
```

The dashboard will be available at: **http://127.0.0.1:8050**

## Quick One-Liner (After Dependencies are Installed)

```bash
python run_app.py
```

## Troubleshooting

If you still get import errors:
1. Make sure you're in the project directory: `cd d:\XU\projects-xlab\bi-platform\bi-platform`
2. Check if you're using a virtual environment (recommended)
3. Verify Python version: `python --version` (should be 3.8+)

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/bi.txt

# Run the app
python run_app.py
```

