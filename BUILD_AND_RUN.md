# Build and Run Guide

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
python setup_and_run.py
```

This will automatically:
- Install all required Python packages
- Create sample data files
- Set up the project structure

### Step 2: Run the Dashboard
```bash
python run_app.py
```

### Step 3: Open in Browser
Navigate to: **http://127.0.0.1:8050**

## Detailed Build Instructions

### Prerequisites Check

Verify you have Python 3.8+:
```bash
python --version
```

### Installation Methods

#### Method 1: Full Installation (Recommended)
```bash
# Install all dependencies
pip install -r requirements/base.txt
pip install -r requirements/bi.txt

# Create sample data
python scripts/create_sample_data.py

# Create necessary directories
mkdir -p logs data
```

#### Method 2: Using Setup Script
```bash
python setup_and_run.py
```

### Running the Application

#### Option A: Using Run Script
```bash
python run_app.py
```

#### Option B: Direct Python Module
```bash
python -m bi_dashboard.app
```

#### Option C: Python Interactive
```python
from bi_dashboard.app import run_server
run_server(debug=True)
```

## Configuration

### Environment Setup

1. **Create `.env` file** (optional, for API Engine):
```env
ENVIRONMENT=dev
SENDGRID_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
# ... other API keys
```

2. **Or edit config files directly**:
   - `configs/dev/api_config.yaml` - API Engine settings
   - `configs/dev/bi_config.yaml` - Dashboard settings

### Port Configuration

To change the port, edit `run_app.py`:
```python
run_server(host="127.0.0.1", port=8080, debug=True)
```

## Verification

### Check Installation

```python
# Test imports
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

## Common Issues & Solutions

### Issue: Port Already in Use
**Solution**: Change port in `run_app.py` or kill the process using port 8050

### Issue: Module Not Found
**Solution**: 
```bash
pip install -r requirements/base.txt
pip install -r requirements/bi.txt
```

### Issue: File Upload Not Working
**Solution**: 
- Ensure file is CSV or Excel format
- Check browser console for errors
- Verify file size (try smaller file first)

### Issue: Charts Not Displaying
**Solution**:
- Check browser console for JavaScript errors
- Verify data columns exist
- Ensure numeric columns for Y-axis

### Issue: Database Connection Fails
**Solution**:
- Verify database is running
- Check credentials in config
- Install appropriate driver (psycopg2 for PostgreSQL)

## Development Mode

### Enable Debug Mode

In `run_app.py` or `bi_dashboard/app.py`:
```python
run_server(debug=True)
```

This enables:
- Hot reloading (auto-refresh on code changes)
- Detailed error messages
- Debug toolbar

### View Logs

Logs are written to:
- Console output (when debug=True)
- `logs/` directory (if configured)

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8050 "bi_dashboard.app:app.server"
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/base.txt -r requirements/bi.txt
COPY . .
CMD ["python", "run_app.py"]
```

### Environment Variables

Set production environment:
```bash
export ENVIRONMENT=prod
```

Update `configs/prod/` files with production settings.

## Testing

### Run Unit Tests
```bash
pytest tests/unit/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Manual Testing Checklist

- [ ] Dashboard loads at http://127.0.0.1:8050
- [ ] File upload works (CSV/Excel)
- [ ] Charts can be created (Line, Bar, Pie, Table)
- [ ] Data preview displays correctly
- [ ] Sample data files exist in `data/` directory

## Next Steps After Running

1. **Upload Sample Data**: Use files from `data/` directory
2. **Create Charts**: Try different chart types
3. **Explore Examples**: Check `examples/` directory
4. **Read Documentation**: See `README.md` and `ANALYSIS.md`

## Support

If you encounter issues:
1. Check `logs/` directory for error logs
2. Review `ANALYSIS.md` for architecture details
3. Verify all dependencies are installed
4. Check Python version (3.8+ required)

