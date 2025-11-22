# BI Platform - Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Option 1: Automated Setup (Recommended)

Run the setup script which will install all dependencies and create sample data:

```bash
python setup_and_run.py
```

This will:
1. Install all required packages
2. Create sample data files
3. Optionally start the dashboard

### Option 2: Manual Setup

1. **Install dependencies:**
```bash
pip install -r requirements/base.txt
pip install -r requirements/bi.txt
```

2. **Create sample data (optional):**
```bash
python scripts/create_sample_data.py
```

3. **Create logs directory:**
```bash
mkdir logs
```

## Running the Application

### Start the Dashboard

```bash
python run_app.py
```

Or directly:
```bash
python -m bi_dashboard.app
```

### Access the Dashboard

Open your web browser and navigate to:
```
http://127.0.0.1:8050
```

## Using the Dashboard

### 1. Upload Data

- Click "Drag and Drop or Select Files"
- Upload a CSV or Excel file
- The data will be automatically loaded and previewed

### 2. Create Charts

1. Select a **Chart Type** (Line, Bar, Pie, or Table)
2. Choose **X-Axis Column** (for line/bar charts)
3. Choose **Y-Axis Column** (for line/bar charts)
   - For Pie charts: X = Names, Y = Values
4. Click **Create Chart**

### 3. Sample Data

If you ran `create_sample_data.py`, you'll have:
- `data/sales_data.csv` - Sales data with dates, regions, products
- `data/employee_data.csv` - Employee information
- `data/time_series_data.csv` - Time series sensor data

## Example Workflows

### Example 1: Visualize Sales Data

1. Upload `data/sales_data.csv`
2. Select Chart Type: **Line Chart**
3. X-Axis: **date**
4. Y-Axis: **sales**
5. Click **Create Chart**

### Example 2: Compare by Region

1. Use the same sales data
2. Select Chart Type: **Bar Chart**
3. X-Axis: **region**
4. Y-Axis: **revenue**
5. Click **Create Chart**

### Example 3: Product Distribution

1. Use sales data
2. Select Chart Type: **Pie Chart**
3. Names: **product**
4. Values: **quantity**
5. Click **Create Chart**

## Using the API Engine

### Basic Usage

```python
from api_engine import APIEngine

# Initialize (reads config from configs/ directory)
engine = APIEngine()

# Send an email
result = engine.send_email(
    to="recipient@example.com",
    subject="Hello",
    content="<h1>Hello World</h1>"
)

# Upload a file
from pathlib import Path
url = engine.upload_file(Path("document.pdf"), bucket="documents")
```

### Configuration

1. Create a `.env` file in the project root:
```env
SENDGRID_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
ENVIRONMENT=dev
```

2. Or edit `configs/dev/api_config.yaml` directly

## Troubleshooting

### Port Already in Use

If port 8050 is already in use, change it in `run_app.py`:
```python
run_server(host="127.0.0.1", port=8051, debug=True)
```

### Missing Dependencies

If you get import errors:
```bash
pip install -r requirements/base.txt
pip install -r requirements/bi.txt
```

### File Upload Issues

- Ensure file is CSV or Excel format
- Check file size (large files may take time)
- Verify file encoding (UTF-8 recommended)

### Database Connection

To connect to a database, you'll need:
- Database server running
- Credentials in config or environment variables
- Appropriate database driver (psycopg2 for PostgreSQL)

## Development

### Project Structure

```
bi-platform/
├── api_engine/          # API Engine module
├── bi_dashboard/        # Dashboard module
├── configs/            # Configuration files
├── examples/           # Usage examples
├── scripts/            # Utility scripts
├── data/              # Sample data (created by script)
└── logs/              # Log files
```

### Running Tests

```bash
pytest tests/
```

### Code Style

The project follows PEP 8. Consider using:
- `black` for formatting
- `flake8` for linting

## Next Steps

1. **Explore Examples**: Check `examples/` directory
2. **Read Documentation**: See `README.md` for detailed docs
3. **Customize**: Modify configs for your needs
4. **Extend**: Add new providers or chart types

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review `ANALYSIS.md` for architecture details
3. See `examples/` for usage patterns

