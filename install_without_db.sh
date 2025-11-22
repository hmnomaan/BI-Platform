#!/bin/bash
# Quick install script for Linux/Mac without database drivers
# This avoids psycopg2-binary build issues if needed

echo "============================================================"
echo "BI Platform - Quick Install (Without Database Drivers)"
echo "============================================================"
echo ""
echo "This will install all dependencies except database drivers."
echo "The platform works fine without them if you only use CSV/Excel files."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

python3 --version

echo ""
echo "Installing base dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/base.txt || {
    echo "Warning: Some dependencies failed to install."
    exit 1
}

echo ""
echo "Installing API Engine dependencies..."
python3 -m pip install -r requirements/api.txt

echo ""
echo "Installing BI Dashboard dependencies..."
python3 -m pip install -r requirements/bi.txt

echo ""
echo "Creating directories..."
mkdir -p logs data

echo ""
echo "Creating sample data..."
python3 scripts/create_sample_data.py

echo ""
echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo "To run the dashboard:"
echo "  python3 run_app.py"
echo ""
echo "The dashboard will be available at: http://127.0.0.1:8050"
echo ""
echo "Note: Database drivers were not installed. If you need them later:"
echo "  pip install -r requirements/database.txt"
echo ""

