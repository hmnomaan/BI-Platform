# BI Platform Integration Guide

## Overview

This guide shows how to integrate BI Platform modules into various frameworks and applications.

## Python Package Installation

### Install from Source

```bash
# Clone or download the package
cd bi-platform

# Install in development mode
pip install -e .

# Or install with all extras
pip install -e ".[all]"
```

### Install as Package

```bash
# Build package
python setup.py sdist bdist_wheel

# Install from built package
pip install dist/bi-platform-1.0.0.tar.gz
```

## Integration Examples

### 1. Django Integration

See `examples/django_integration.py` for complete example.

**Key Points:**
- Initialize `StandardizedAPIEngine` in Django settings or as module-level variable
- Use in views, models, or management commands
- All methods return standardized dict responses

**Example View:**
```python
from api_engine.core.standardized_interface import StandardizedAPIEngine

api_engine = StandardizedAPIEngine()

def send_notification(request):
    result = api_engine.send_email({
        "to": request.user.email,
        "subject": "Notification",
        "content": "Hello!"
    })
    return JsonResponse(result)
```

### 2. Flask Integration

See `examples/flask_integration.py` for complete example.

**Example Route:**
```python
from flask import Flask, request, jsonify
from api_engine.core.standardized_interface import StandardizedAPIEngine

app = Flask(__name__)
api_engine = StandardizedAPIEngine()

@app.route('/api/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    result = api_engine.send_email(data)
    return jsonify(result)
```

### 3. FastAPI Integration

The package includes a built-in FastAPI service:

```python
# Run HTTP service
python -m api_engine.http_service

# Or use in your FastAPI app
from api_engine.http_service import app
from api_engine.core.standardized_interface import StandardizedAPIEngine

api_engine = StandardizedAPIEngine()

@app.post("/custom-endpoint")
async def custom_endpoint():
    result = api_engine.send_email({...})
    return result
```

### 4. Standalone Python Script

```python
from pathlib import Path
from api_engine.core.standardized_interface import StandardizedAPIEngine

# Initialize
engine = StandardizedAPIEngine()

# Send email
result = engine.send_email({
    "to": "user@example.com",
    "subject": "Hello",
    "content": "Message"
})

# Upload file
result = engine.upload_file(
    Path("document.pdf"),
    {"bucket": "documents"}
)
```

### 5. BI Dashboard Integration

```python
from bi_dashboard.core.data_connector import DataSourceManager
from bi_dashboard.components.dashboard import Dashboard
from pathlib import Path

# Load data
manager = DataSourceManager()
df = manager.read_file(Path("data.csv"), "csv")

# Create dashboard
dashboard = Dashboard()
dashboard.add_chart("line", df, {
    "x_axis": "date",
    "y_axis": "sales"
})

# Export chart
from bi_dashboard.core.export import ChartExporter
exporter = ChartExporter()
fig = dashboard.chart_builder.chart_builder.create_chart(...)
exporter.export_image(fig, Path("chart.png"))
```

## Configuration

### Environment Variables

Set in `.env` file or environment:

```env
ENVIRONMENT=dev
SENDGRID_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### YAML Configuration

Edit `configs/dev/api_config.yaml`:

```yaml
providers:
  email:
    type: sendgrid
    api_key: ${SENDGRID_API_KEY}
```

## Standardized Interface Pattern

All functions follow this pattern:

```python
# Input: dict or Path
result = function(input_dict_or_path, params_dict)

# Output: dict with status
{
    "status": "success" | "error",
    # ... result data ...
    "error": Optional[str]  # if status == "error"
}
```

## Error Handling

Always check the `status` field:

```python
result = api_engine.send_email({...})

if result["status"] == "success":
    # Handle success
    message_id = result["message_id"]
else:
    # Handle error
    error = result["error"]
    # Log, retry, or notify
```

## Best Practices

1. **Initialize Once**: Create API engine instance once and reuse
2. **Error Handling**: Always check `status` field
3. **Logging**: API calls are automatically logged
4. **Retry**: Built-in retry with exponential backoff
5. **Configuration**: Use YAML files, not hardcoded values

## Testing

```python
# Mock providers for testing
from unittest.mock import Mock

api_engine.engine.email_provider = Mock()
api_engine.engine.email_provider.send_email.return_value = {
    "status": "success",
    "message_id": "test-123"
}
```

## Troubleshooting

### Import Errors

```bash
# Ensure package is installed
pip install -e .

# Check Python path
python -c "import api_engine; print(api_engine.__file__)"
```

### Configuration Issues

- Check `configs/dev/api_config.yaml` exists
- Verify environment variables are set
- Check file permissions

### API Call Failures

- Check logs in `logs/api_call_logs.jsonl`
- Verify API keys are correct
- Check network connectivity
- Review retry logs

## Next Steps

- See `docs/API_REFERENCE.md` for detailed API documentation
- Check `examples/` for more integration examples
- Review `README.md` for general usage

