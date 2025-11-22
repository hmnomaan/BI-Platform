# BI Platform - Developer Guide

Complete guide for developers working on or extending the BI Platform.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Code Architecture](#code-architecture)
4. [Development Workflow](#development-workflow)
5. [Adding New Features](#adding-new-features)
6. [Testing](#testing)
7. [Code Standards](#code-standards)
8. [Debugging](#debugging)
9. [Contributing](#contributing)

## Development Setup

### Prerequisites

- **Python 3.8+** (3.9 or 3.10 recommended)
- **Git** for version control
- **Virtual environment** (recommended)
- **IDE**: VS Code, PyCharm, or any Python IDE

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd bi-platform

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install development dependencies
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
pip install -r requirements/dev.txt

# 5. Install package in development mode
pip install -e .
```

### Development Tools

```bash
# Code formatting
pip install black flake8 mypy

# Testing
pip install pytest pytest-cov

# Pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## Project Structure

```
bi-platform/
├── api_engine/              # API Engine module
│   ├── __init__.py
│   ├── http_service.py      # FastAPI REST API
│   ├── core/                # Core functionality
│   │   ├── api_engine.py    # Main orchestrator
│   │   ├── config_manager.py
│   │   ├── abstract_providers.py
│   │   └── ...
│   ├── providers/           # Provider implementations
│   │   ├── email_providers.py
│   │   ├── storage_providers.py
│   │   └── ...
│   └── utils/               # Utilities
│       ├── logging.py
│       └── security.py
│
├── bi_dashboard/            # BI Dashboard module
│   ├── __init__.py
│   ├── app.py              # Dash application entry
│   ├── core/               # Core functionality
│   │   ├── data_connector.py
│   │   ├── viz_engine.py
│   │   └── ...
│   ├── components/         # UI components
│   │   ├── dashboard.py
│   │   ├── chart_builder.py
│   │   └── data_source.py
│   └── utils/              # Utilities
│
├── configs/                 # Configuration files
│   ├── dev/
│   ├── prod/
│   └── shared_config.yaml
│
├── tests/                   # Test files
│   ├── unit/
│   └── integration/
│
├── examples/                # Example code
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── requirements/            # Dependencies
```

## Code Architecture

### API Engine Architecture

**Design Pattern**: Provider Pattern + Facade Pattern

```
APIEngine (Facade)
    ↓
AbstractProvider (Base)
    ↓
┌─────────────┬──────────────┬─────────────┐
│ Email       │ Storage      │ Signing     │
│ Provider    │ Provider     │ Provider    │
└─────────────┴──────────────┴─────────────┘
```

**Key Classes**:
- `APIEngine`: Main facade, orchestrates all providers
- `AbstractProvider`: Base class for all providers
- Provider classes: Implement specific service integrations

**Adding a New Provider**:

1. Create provider class in `api_engine/providers/`
2. Inherit from `AbstractProvider`
3. Implement required methods
4. Register in `APIEngine.__init__()`

Example:
```python
# api_engine/providers/new_provider.py
from ..core.abstract_providers import AbstractProvider

class NewProvider(AbstractProvider):
    def __init__(self, config):
        super().__init__(config)
    
    def send(self, data):
        # Implementation
        pass
```

### BI Dashboard Architecture

**Design Pattern**: Component-Based + MVC-like

```
app.py (Controller)
    ↓
┌──────────────┬──────────────┬──────────────┐
│ Dashboard    │ DataSource   │ ChartBuilder │
│ (View)       │ (Model)      │ (View)       │
└──────────────┴──────────────┴──────────────┘
```

**Key Components**:
- `app.py`: Main Dash application, handles routing
- `Dashboard`: Assembles UI components
- `DataSourceManager`: Handles data loading
- `ChartBuilder`: Creates visualizations
- `VizEngine`: Low-level chart generation

## Development Workflow

### 1. Creating a Feature Branch

```bash
git checkout -b feature/new-feature-name
```

### 2. Making Changes

- Follow coding standards (see [Code Standards](#code-standards))
- Write tests for new features
- Update documentation

### 3. Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_api_engine.py

# Run with coverage
pytest --cov=api_engine --cov=bi_dashboard tests/
```

### 4. Code Quality Checks

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy api_engine bi_dashboard
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: Add new feature description"
```

**Commit Message Format**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes

### 6. Push and Create PR

```bash
git push origin feature/new-feature-name
```

## Adding New Features

### Adding a New API Provider

1. **Create Provider Class**:

```python
# api_engine/providers/new_service_provider.py
from typing import Dict, Any
from ..core.abstract_providers import AbstractProvider

class NewServiceProvider(AbstractProvider):
    """Provider for New Service integration."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
    
    def send(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data to New Service."""
        # Implementation
        return {"status": "success"}
```

2. **Register in APIEngine**:

```python
# api_engine/core/api_engine.py
from ..providers.new_service_provider import NewServiceProvider

class APIEngine:
    def __init__(self):
        # ...
        self.new_service = NewServiceProvider(config)
```

3. **Add to HTTP Service**:

```python
# api_engine/http_service.py
@app.post("/api/v1/new-service/action")
async def new_service_action(request: RequestModel):
    result = api_engine.new_service.send(request.dict())
    return result
```

4. **Update Configuration**:

```yaml
# configs/dev/api_config.yaml
new_service:
  enabled: true
  api_key: ${NEW_SERVICE_API_KEY}
```

### Adding a New Chart Type

1. **Add to VizEngine**:

```python
# bi_dashboard/core/viz_engine.py
def create_scatter_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
    """Create scatter plot."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data[config['x_axis']],
        y=data[config['y_axis']],
        mode='markers'
    ))
    return fig
```

2. **Update ChartBuilder**:

```python
# bi_dashboard/core/viz_engine.py
def build_chart(self, chart_type: str, data: pd.DataFrame, config: Dict):
    if chart_type == "scatter":
        return self.create_scatter_chart(data, config)
    # ...
```

3. **Update UI**:

```python
# bi_dashboard/app.py
options=[
    # ...
    {"label": "Scatter Plot", "value": "scatter"}
]
```

## Testing

### Unit Tests

Create test files in `tests/unit/`:

```python
# tests/unit/test_new_feature.py
import pytest
from api_engine.core.api_engine import APIEngine

def test_new_feature():
    engine = APIEngine()
    result = engine.new_service.send({"data": "test"})
    assert result["status"] == "success"
```

### Integration Tests

Create test files in `tests/integration/`:

```python
# tests/integration/test_api_workflow.py
import pytest
from fastapi.testclient import TestClient
from api_engine.http_service import app

client = TestClient(app)

def test_api_endpoint():
    response = client.post("/api/v1/new-service/action", json={"data": "test"})
    assert response.status_code == 200
```

### Running Tests

```bash
# All tests
pytest

# Specific test
pytest tests/unit/test_api_engine.py::test_send_email

# With coverage
pytest --cov=. --cov-report=html
```

## Code Standards

### Python Style Guide

- Follow **PEP 8**
- Use **type hints** for all function signatures
- Write **docstrings** for all classes and functions
- Maximum line length: **120 characters**

### Example Code Structure

```python
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MyClass:
    """
    Class description.
    
    Attributes:
        attribute1: Description of attribute1
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize MyClass.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def my_method(self, param: str) -> Dict[str, Any]:
        """Method description.
        
        Args:
            param: Parameter description
        
        Returns:
            Result dictionary
        
        Raises:
            ValueError: If param is invalid
        """
        if not param:
            raise ValueError("param cannot be empty")
        
        return {"status": "success"}
```

### Import Organization

```python
# Standard library imports
import os
from pathlib import Path
from typing import Dict, Any

# Third-party imports
import pandas as pd
from dash import html

# Local imports
from .core.api_engine import APIEngine
from ..utils.helpers import get_logger
```

## Debugging

### Logging

```python
from ..utils.helpers import get_logger

logger = get_logger("MyModule")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Debug Mode

```bash
# Run dashboard in debug mode
python run_app.py  # debug=True by default

# Run API in debug mode
python run_api.py  # reload=True in uvicorn
```

### Using Python Debugger

```python
import pdb

def my_function():
    pdb.set_trace()  # Breakpoint here
    # Your code
```

## Contributing

### Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] All tests pass

### Code Review Guidelines

- Be respectful and constructive
- Focus on code, not person
- Ask questions if unclear
- Suggest improvements
- Approve if code meets standards

## Common Tasks

### Adding Configuration

1. Add to `configs/shared_config.yaml` or environment-specific config
2. Use `ConfigManager` to load
3. Access via `config.get('section.key')`

### Adding Dependencies

1. Add to appropriate `requirements/*.txt` file
2. Pin version: `package==1.2.3`
3. Update `setup.py` if needed
4. Document in relevant guide

### Database Migrations

Currently not implemented. For future:
- Use Alembic for SQLAlchemy migrations
- Create migration scripts in `migrations/` directory

## Resources

- [API Documentation](API_DOCUMENTATION.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Testing Guide](tests/README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dash Documentation](https://dash.plotly.com/)

---

**Need Help?** Open an issue or check existing documentation.

