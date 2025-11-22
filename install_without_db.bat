@echo off
REM Quick install script for Windows without database drivers
REM This avoids psycopg2-binary build issues

echo ============================================================
echo BI Platform - Quick Install (Without Database Drivers)
echo ============================================================
echo.
echo This will install all dependencies except database drivers.
echo The platform works fine without them if you only use CSV/Excel files.
echo.

python --version
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo.
echo Installing base dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements/base.txt
if errorlevel 1 (
    echo Warning: Some dependencies failed to install.
    pause
    exit /b 1
)

echo.
echo Installing API Engine dependencies...
python -m pip install -r requirements/api.txt

echo.
echo Installing BI Dashboard dependencies...
python -m pip install -r requirements/bi.txt

echo.
echo Creating directories...
if not exist logs mkdir logs
if not exist data mkdir data

echo.
echo Creating sample data...
python scripts/create_sample_data.py

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo To run the dashboard:
echo   python run_app.py
echo.
echo The dashboard will be available at: http://127.0.0.1:8050
echo.
echo Note: Database drivers were not installed. If you need them later:
echo   pip install -r requirements/database.txt
echo.
pause

