# BI Platform

A comprehensive Business Intelligence platform with a modular API engine and interactive dashboard capabilities.

## Overview

This platform consists of two main components:

1. **API Engine**: A modular system for integrating with various third-party services (email, storage, e-signatures, search, physical mail)
2. **BI Dashboard**: An interactive dashboard built with Dash/Plotly for data visualization and analysis

## Features

### API Engine
- **Email Providers**: SendGrid, Mailgun
- **Storage Providers**: AWS S3, Azure Blob Storage
- **E-Signature Providers**: DocuSign
- **Search Providers**: Elasticsearch
- **Physical Mail Providers**: Lob.com
- **Modular Architecture**: Easy to add new providers
- **Configuration Management**: YAML-based configuration with environment variable overrides
- **Security**: Password hashing, encryption utilities, API key generation

### BI Dashboard
- **Data Connectors**: Database (PostgreSQL/MySQL), CSV/Excel files, REST APIs
- **Visualization Engine**: Line charts, bar charts, pie charts, scatter plots, data tables
- **Interactive Features**: Filters, drill-down, cross-filtering
- **Performance Optimization**: DataFrame caching, memory optimization
- **Responsive Design**: Bootstrap-based UI with custom styling

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd bi-platform

# Run automated setup
python setup_and_run.py
```

### Option 2: Using Makefile

```bash
make setup    # Full setup (install + sample data)
make run      # Run the dashboard
```

### Option 3: Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd bi-platform
```

2. Install dependencies:
```bash
pip install -r requirements/base.txt
pip install -r requirements/api.txt
pip install -r requirements/bi.txt
```

3. Create sample data:
```bash
python scripts/create_sample_data.py
```

4. Run the application:
```bash
python run_app.py
```

Access the dashboard at: **http://127.0.0.1:8050**

## Installation

### Prerequisites
- Python 3.8+ (3.9 or 3.10 recommended)
- pip
- (Optional) Docker and Docker Compose for containerized deployment

**Windows Users**: If you encounter issues with `psycopg2-binary`, see [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md). Database drivers are optional - the platform works without them if you only use CSV/Excel files.

### Detailed Installation

See [BUILD.md](BUILD.md) for comprehensive build and installation instructions.

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Configuration

### Environment Variables

Create a `.env` file in the project root with your API keys and credentials:

```env
# Email
SENDGRID_API_KEY=your_sendgrid_key
MAILGUN_API_KEY=your_mailgun_key
MAILGUN_DOMAIN=your_domain

# Storage
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

# E-Signature
DOCUSIGN_API_KEY=your_docusign_key
DOCUSIGN_ACCOUNT_ID=your_account_id
DOCUSIGN_USER_ID=your_user_id

# Search
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=password

# Physical Mail
LOB_API_KEY=your_lob_key

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bi_platform
DB_USER=postgres
DB_PASSWORD=password

# Environment
ENVIRONMENT=dev  # or prod
```

### Configuration Files

Configuration files are located in the `configs/` directory:
- `shared_config.yaml`: Common settings
- `dev/api_config.yaml`: Development API configuration
- `dev/bi_config.yaml`: Development BI configuration
- `prod/api_config.yaml`: Production API configuration
- `prod/bi_config.yaml`: Production BI configuration

## Usage

### API Engine

```python
from api_engine.core.api_engine import APIEngine
from pathlib import Path

# Initialize the engine
engine = APIEngine()

# Send an email
result = engine.send_email(
    to="recipient@example.com",
    subject="Hello",
    content="<h1>Hello World</h1>"
)

# Upload a file
url = engine.upload_file(Path("document.pdf"), bucket="documents")

# Create an e-signature envelope
envelope_id = engine.create_envelope(
    document=Path("contract.pdf"),
    signers=[
        {"email": "signer@example.com", "name": "John Doe"}
    ]
)
```

See `examples/api_engine_usage.py` for more examples.

### BI Dashboard

```python
from bi_dashboard.core.data_connector import DataSourceManager
from bi_dashboard.components.dashboard import Dashboard
import pandas as pd

# Initialize components
data_manager = DataSourceManager()
dashboard = Dashboard()

# Load data from CSV
df = data_manager.read_csv_excel(Path("data.csv"))

# Add a chart
dashboard.add_chart(
    chart_type="line",
    data=df,
    config={
        "x_axis": "date",
        "y_axis": "sales",
        "title": "Sales Over Time"
    }
)

# Build and display dashboard
layout = dashboard.build_layout()
```

See `examples/bi_dashboard_usage.py` for more examples.

### Running the Dashboard Server

```python
from bi_dashboard.app import run_server

# Run the server
run_server(host="127.0.0.1", port=8050, debug=True)
```

Or from command line:
```bash
python -m bi_dashboard.app
```

## Project Structure

```
bi-platform/
├── api_engine/           # API Engine module
│   ├── core/             # Core engine and configuration
│   ├── providers/        # Provider implementations
│   └── utils/            # Utilities (logging, security)
├── bi_dashboard/         # BI Dashboard module
│   ├── components/       # Dashboard components
│   ├── core/            # Core functionality
│   ├── assets/          # CSS and static assets
│   └── utils/           # Utilities
├── configs/              # Configuration files
│   ├── dev/             # Development configs
│   └── prod/            # Production configs
├── examples/             # Usage examples
├── tests/               # Test files
├── scripts/             # Utility scripts
└── requirements/        # Python dependencies
```

## Documentation

### 📚 Complete Knowledge Book

**Start Here**: **[KNOWLEDGE_BOOK.md](KNOWLEDGE_BOOK.md)** - The ultimate guide covering everything from beginner basics to advanced architecture

### 📑 Documentation Index

- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation index with links to all guides

### 🚀 Quick Start & User Guides

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide (5 minutes)
- **[QUICK_RUN.md](QUICK_RUN.md)** - Quick reference for running the platform
- **[END_TO_END_GUIDE.md](END_TO_END_GUIDE.md)** - Complete end-to-end setup and usage guide
- **[BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)** - Guide for beginners and non-coders

### 👨‍💻 Developer Documentation

- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Complete developer guide with development steps
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference with all endpoints
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture documentation

### ☁️ Deployment & Cloud

- **[BUILD.md](BUILD.md)** - Complete build and installation guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide for various environments
- **[CLOUD_GUIDE.md](CLOUD_GUIDE.md)** - Cloud deployment guide (AWS, Azure, GCP)

### 🗺️ Future Development

- **[ROADMAP.md](ROADMAP.md)** - Development roadmap and future plans

### 📖 Additional Documentation

- **[docs/](docs/)** - Detailed documentation
  - API Reference
  - Integration Guides
  - User Guides

## Development

### Running Tests

```bash
# All tests
pytest tests/

# Or using Makefile
make test
make test-unit      # Unit tests only
make test-integration  # Integration tests only
```

### Code Style

The project follows PEP 8 style guidelines. Use the Makefile:

```bash
make format    # Format code with black
make lint      # Run linter
make check     # Run all checks
```

Or manually:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] Add more provider implementations
- [ ] Enhanced dashboard interactivity
- [ ] Real-time data updates
- [ ] Advanced analytics features
- [ ] User authentication and authorization
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Webhook support

