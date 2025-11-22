# BI Platform - Troubleshooting Guide

Common issues and solutions for the BI Platform.

## Table of Contents

1. [API Documentation Not Loading](#api-documentation-not-loading)
2. [Dashboard Not Starting](#dashboard-not-starting)
3. [Import Errors](#import-errors)
4. [Port Already in Use](#port-already-in-use)
5. [Database Connection Issues](#database-connection-issues)
6. [File Upload Issues](#file-upload-issues)
7. [Chart Display Issues](#chart-display-issues)

## API Documentation Not Loading

### Issue: `/docs` page shows blank or nothing

**Symptoms**:
- Server returns 200 OK for `/docs`
- Browser shows blank page
- Console shows errors loading static assets

**Solutions**:

#### Solution 1: Check FastAPI Version

```bash
pip install --upgrade fastapi uvicorn
```

#### Solution 2: Try Different Browser

Sometimes browser extensions or settings can block the docs:
- Try Chrome/Firefox/Edge
- Disable ad blockers
- Try incognito/private mode

#### Solution 3: Check Browser Console

Open browser developer tools (F12) and check:
- Console tab for JavaScript errors
- Network tab for failed requests
- Look for CORS errors

#### Solution 4: Access OpenAPI JSON Directly

Try accessing the OpenAPI schema:
```
http://localhost:8000/openapi.json
```

If this works, the issue is with the Swagger UI rendering.

#### Solution 5: Use ReDoc Instead

Try the alternative documentation:
```
http://localhost:8000/redoc
```

#### Solution 6: Check Server Logs

Look for errors in server logs:
```bash
# Check for errors when accessing /docs
# Look for missing static files or CORS issues
```

#### Solution 7: Restart Server

Sometimes a restart fixes the issue:
```bash
# Stop server (Ctrl+C)
# Restart
python run_api.py
```

#### Solution 8: Check Network/Firewall

- Ensure no firewall is blocking static assets
- Check if you're behind a proxy
- Try accessing from different network

### Issue: `/docs` returns 404

**Solution**: Make sure docs are enabled in FastAPI:

```python
app = FastAPI(
    docs_url="/docs",  # Enable Swagger UI
    redoc_url="/redoc"  # Enable ReDoc
)
```

## Dashboard Not Starting

### Issue: Dashboard won't start

**Solutions**:

1. **Check Port**: Port 8050 might be in use
   ```bash
   # Find process using port
   # Windows:
   netstat -ano | findstr :8050
   # Linux/Mac:
   lsof -i :8050
   ```

2. **Check Dependencies**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements/base.txt
   pip install -r requirements/bi.txt
   ```

3. **Check Python Version**: Need Python 3.8+
   ```bash
   python --version
   ```

4. **Check Logs**: Look for error messages
   ```bash
   python run_app.py
   # Check error output
   ```

## Import Errors

### Issue: `ModuleNotFoundError`

**Solutions**:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements/base.txt
   pip install -r requirements/api.txt
   pip install -r requirements/bi.txt
   ```

2. **Install Package in Development Mode**:
   ```bash
   pip install -e .
   ```

3. **Check Virtual Environment**: Make sure venv is activated
   ```bash
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

4. **Check PYTHONPATH**: Add project root to path
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

## Port Already in Use

### Issue: Port 8050 or 8000 already in use

**Solutions**:

1. **Find and Kill Process**:
   ```bash
   # Windows:
   netstat -ano | findstr :8050
   taskkill /PID <PID> /F
   
   # Linux/Mac:
   lsof -i :8050
   kill -9 <PID>
   ```

2. **Change Port**:
   ```python
   # In run_app.py
   run_server(host="127.0.0.1", port=8051, debug=True)
   
   # In run_api.py or http_service.py
   uvicorn.run(app, host="0.0.0.0", port=8001)
   ```

## Database Connection Issues

### Issue: Can't connect to database

**Solutions**:

1. **Check Database is Running**:
   ```bash
   # PostgreSQL
   psql -h localhost -U postgres
   
   # MySQL
   mysql -h localhost -u root -p
   ```

2. **Check Credentials**: Verify in config or `.env`
   ```yaml
   # configs/dev/bi_config.yaml
   database:
     host: localhost
     port: 5432
     name: bi_platform
     user: postgres
     password: your_password
   ```

3. **Install Database Driver**:
   ```bash
   # PostgreSQL
   pip install psycopg2-binary
   
   # MySQL
   pip install pymysql
   ```

4. **Check Network**: Ensure database is accessible
   ```bash
   telnet localhost 5432
   ```

## File Upload Issues

### Issue: File upload fails or data not loading

**Solutions**:

1. **Check File Format**: Must be CSV or Excel
   - CSV: `.csv`
   - Excel: `.xlsx` or `.xls`

2. **Check File Size**: Large files may timeout
   - Try smaller file first
   - Check file size limits

3. **Check File Encoding**: Use UTF-8
   - Open in text editor
   - Save as UTF-8

4. **Check Browser Console**: Look for JavaScript errors
   - Press F12
   - Check Console tab

5. **Check File Structure**: Ensure proper format
   - First row should have column names
   - No empty rows at top
   - Consistent data types

## Chart Display Issues

### Issue: Charts don't display or show errors

**Solutions**:

1. **Check Data Columns**: Ensure columns exist
   - Verify column names match
   - Check for typos

2. **Check Data Types**: Y-axis needs numeric data
   - Ensure numeric columns for Y-axis
   - Check for non-numeric values

3. **Check Browser Console**: Look for JavaScript errors
   - Press F12
   - Check Console tab for errors

4. **Check Plotly Version**: Ensure compatible version
   ```bash
   pip install plotly>=5.10.0
   ```

5. **Try Different Chart Type**: Test with simple chart first
   - Start with table view
   - Then try line chart
   - Progress to more complex charts

## General Troubleshooting Steps

### 1. Check Logs

```bash
# Application logs
tail -f logs/bi_platform.log

# Docker logs
docker-compose logs -f
```

### 2. Validate Installation

```bash
python scripts/validate_deployment.py
```

### 3. Test Imports

```python
# Test API Engine
python -c "from api_engine import APIEngine; print('OK')"

# Test Dashboard
python -c "from bi_dashboard import app; print('OK')"
```

### 4. Check Configuration

```bash
# Verify config files exist
ls configs/dev/

# Check environment variables
cat .env
```

### 5. Restart Services

```bash
# Stop all services
# Restart
python run_app.py  # Dashboard
python run_api.py  # API
```

## Getting Help

If issues persist:

1. **Check Documentation**:
   - [BUILD.md](BUILD.md) - Build issues
   - [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) - Windows issues
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment issues

2. **Check Examples**:
   - Review `examples/` directory
   - Try sample code

3. **Check GitHub Issues**:
   - Search existing issues
   - Create new issue with details

4. **Provide Information**:
   - Python version
   - Operating system
   - Error messages
   - Steps to reproduce

---

**Remember**: Most issues are resolved by:
1. Checking dependencies are installed
2. Verifying configuration
3. Checking logs for errors
4. Restarting services

