# BI Platform - System Architecture

Complete technical architecture documentation for the BI Platform.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)
7. [Scalability](#scalability)
8. [Security Architecture](#security-architecture)

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BI Platform                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐      │
│  │  BI Dashboard    │      │   API Engine     │      │
│  │  (Port 8050)     │      │   (Port 8000)    │      │
│  └──────────────────┘      └──────────────────┘      │
│           │                        │                   │
│           └────────────┬───────────┘                   │
│                        │                                │
│              ┌─────────▼─────────┐                     │
│              │  Shared Services  │                     │
│              │  - Config Manager │                     │
│              │  - Logging        │                     │
│              │  - Security       │                     │
│              └───────────────────┘                     │
│                        │                                │
└────────────────────────┼───────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ Database│    │  Files  │    │ External│
    │ (Postgres│    │ (CSV/XLS)│    │ APIs    │
    │  /MySQL) │    │         │    │         │
    └─────────┘    └─────────┘    └─────────┘
```

### Components

1. **BI Dashboard**: Web-based data visualization interface
2. **API Engine**: RESTful API for third-party service integration
3. **Shared Services**: Common utilities (config, logging, security)

## Architecture Patterns

### 1. Provider Pattern

**Purpose**: Enable easy addition of new service providers

**Implementation**:
```
AbstractProvider (Base Class)
    ↓
┌──────────────┬──────────────┬──────────────┐
│ Email        │ Storage      │ Signing      │
│ Provider     │ Provider     │ Provider     │
└──────────────┴──────────────┴──────────────┘
```

**Benefits**:
- Easy to add new providers
- Consistent interface
- Provider can be swapped without code changes

### 2. Facade Pattern

**Purpose**: Simplified interface to complex subsystems

**Implementation**:
```
APIEngine (Facade)
    ↓
Provides simple interface
    ↓
Coordinates multiple providers
```

**Benefits**:
- Simple API for clients
- Hides complexity of provider management
- Centralized error handling

### 3. Component-Based Architecture

**Purpose**: Modular, reusable UI components

**Implementation**:
```
Dashboard (Container)
    ↓
┌─────────────┬─────────────┬─────────────┐
│ DataSource  │ ChartBuilder│ Filters     │
│ Component   │ Component   │ Component   │
└─────────────┴─────────────┴─────────────┘
```

**Benefits**:
- Reusable components
- Easy to test
- Clear separation of concerns

### 4. MVC-like Pattern (Dashboard)

**Purpose**: Separate data, presentation, and control

**Implementation**:
```
Model:      DataSourceManager (data)
View:       Dashboard Components (presentation)
Controller: app.py callbacks (control)
```

## Component Architecture

### API Engine

```
api_engine/
├── core/
│   ├── api_engine.py          # Facade/Orchestrator
│   ├── config_manager.py       # Configuration management
│   ├── abstract_providers.py   # Base provider class
│   ├── standardized_interface.py # Interface contracts
│   └── retry_handler.py        # Retry logic
│
├── providers/
│   ├── email_providers.py      # SendGrid, Mailgun
│   ├── storage_providers.py    # S3, Azure Blob
│   ├── signing_providers.py    # DocuSign
│   ├── search_providers.py     # Elasticsearch
│   └── physical_mail_providers.py # Lob
│
├── utils/
│   ├── logging.py              # Logging utilities
│   └── security.py             # Security utilities
│
└── http_service.py             # FastAPI REST API
```

**Class Hierarchy**:
```
APIEngine
    ├── EmailProvider (AbstractProvider)
    │   ├── SendGridProvider
    │   └── MailgunProvider
    ├── StorageProvider (AbstractProvider)
    │   ├── S3Provider
    │   └── AzureBlobProvider
    └── ...
```

### BI Dashboard

```
bi_dashboard/
├── app.py                      # Dash application entry
│
├── core/
│   ├── data_connector.py       # Data loading (Model)
│   ├── viz_engine.py          # Chart generation (View)
│   ├── interactivity.py       # Callbacks/Interactions
│   ├── chart_linkage.py       # Chart linking
│   └── export.py              # Chart export
│
├── components/
│   ├── dashboard.py           # Main dashboard
│   ├── chart_builder.py       # Chart components
│   └── data_source.py         # Data source UI
│
└── utils/
    ├── helpers.py             # Utility functions
    └── performance.py         # Performance optimizations
```

**Data Flow**:
```
User Upload → DataSourceComponent
    ↓
DataConnector (loads data)
    ↓
Pandas DataFrame
    ↓
ChartBuilder (creates chart)
    ↓
VizEngine (generates Plotly figure)
    ↓
Dash Graph (displays in browser)
```

## Data Flow

### Dashboard Data Flow

```
1. User uploads CSV file
   ↓
2. File parsed → Pandas DataFrame
   ↓
3. Data preview shown in table
   ↓
4. User selects chart type & columns
   ↓
5. ChartBuilder creates Plotly figure
   ↓
6. Figure rendered as Dash Graph
   ↓
7. Interactive chart displayed
```

### API Request Flow

```
1. Client sends HTTP request
   ↓
2. FastAPI routes request
   ↓
3. Request validated (Pydantic)
   ↓
4. APIEngine method called
   ↓
5. Appropriate provider selected
   ↓
6. Provider executes request
   ↓
7. Response formatted & returned
   ↓
8. Client receives JSON response
```

### Configuration Flow

```
Environment Variables
    ↓
configs/{env}/*.yaml
    ↓
ConfigManager.load()
    ↓
Provider initialization
    ↓
Runtime configuration
```

## Technology Stack

### Backend

- **Python 3.8+**: Core language
- **FastAPI**: REST API framework
- **Dash/Plotly**: Web dashboard framework
- **Pandas**: Data manipulation
- **SQLAlchemy**: Database ORM

### Frontend

- **Dash**: Python web framework (no JavaScript needed)
- **Plotly.js**: Chart rendering
- **Bootstrap**: UI styling
- **Dash Bootstrap Components**: Pre-built UI components

### Infrastructure

- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Uvicorn**: ASGI server for FastAPI
- **Gunicorn**: WSGI server for production

### Third-Party Services

- **SendGrid/Mailgun**: Email services
- **AWS S3/Azure Blob**: Cloud storage
- **DocuSign**: E-signature
- **Elasticsearch**: Search
- **Lob.com**: Physical mail

## Design Decisions

### Why Provider Pattern?

**Decision**: Use Provider Pattern for service integrations

**Rationale**:
- Easy to add new providers
- Swap providers without code changes
- Consistent interface
- Testable in isolation

### Why FastAPI for API?

**Decision**: Use FastAPI for REST API

**Rationale**:
- Automatic API documentation
- Fast performance
- Type validation (Pydantic)
- Async support
- Modern Python features

### Why Dash for Dashboard?

**Decision**: Use Dash for dashboard UI

**Rationale**:
- Pure Python (no JavaScript)
- Built-in Plotly integration
- Interactive by default
- Easy to customize
- Good documentation

### Why YAML for Configuration?

**Decision**: Use YAML + environment variables

**Rationale**:
- Human-readable
- Hierarchical structure
- Environment variable overrides
- Easy to version control

### Why Separate Modules?

**Decision**: Separate API Engine and BI Dashboard

**Rationale**:
- Independent scaling
- Different use cases
- Can deploy separately
- Clear separation of concerns

## Scalability

### Current Limitations

- Single-threaded dashboard server
- In-memory data storage
- No caching layer
- No load balancing

### Scalability Solutions

#### Horizontal Scaling

```
Load Balancer
    ↓
┌───────┬───────┬───────┐
│ App 1 │ App 2 │ App 3 │
└───────┴───────┴───────┘
```

#### Database Scaling

```
Read Replicas
    ↓
┌───────────┬───────────┐
│ Primary   │ Replica   │
│ (Write)   │ (Read)    │
└───────────┴───────────┘
```

#### Caching Layer

```
Redis Cache
    ↓
┌─────────────┐
│ Dashboard   │
│ (Fast)      │
└─────────────┘
```

### Performance Optimization

1. **DataFrame Caching**: Cache processed DataFrames
2. **Lazy Loading**: Load data on demand
3. **Query Optimization**: Optimize database queries
4. **CDN**: Use CDN for static assets

## Security Architecture

### Current Security Features

1. **Configuration Management**: Secrets in config files (not code)
2. **Environment Variables**: Sensitive data in .env
3. **Password Hashing**: Security utilities for hashing
4. **API Key Management**: Provider keys secured

### Security Best Practices

1. **Never commit secrets**: Use .env files
2. **Use HTTPS**: In production
3. **Validate inputs**: Pydantic validation
4. **Error handling**: Don't expose internals
5. **Logging**: Log security events

### Future Security Enhancements

- [ ] API key authentication
- [ ] OAuth 2.0 support
- [ ] Rate limiting
- [ ] Request signing
- [ ] Audit logging

## Deployment Architecture

### Development

```
Single Machine
├── Dashboard (Port 8050)
├── API Engine (Port 8000)
└── Database (Port 5432)
```

### Production (Recommended)

```
Internet
    ↓
Load Balancer
    ↓
┌──────────────────┬──────────────────┐
│  Dashboard App   │   API Engine     │
│  (Multiple)      │   (Multiple)     │
└──────────────────┴──────────────────┘
    ↓                    ↓
┌─────────────────────────────┐
│    Database (Postgres)      │
│    + Redis Cache            │
└─────────────────────────────┘
```

### Docker Architecture

```
docker-compose.yml
├── bi-dashboard (service)
├── api-engine (service)
└── postgres (service)
```

## Monitoring & Observability

### Current Monitoring

- **Logging**: Structured logging with Loguru
- **Health Checks**: /health endpoints
- **Error Tracking**: Exception logging

### Recommended Monitoring

1. **Application Metrics**: Response times, error rates
2. **Infrastructure Metrics**: CPU, memory, disk
3. **Log Aggregation**: ELK Stack or similar
4. **Alerting**: PagerDuty, Slack alerts

## Future Architecture Enhancements

### Planned Improvements

1. **Microservices**: Split into smaller services
2. **Message Queue**: Add async task processing
3. **API Gateway**: Centralized API management
4. **Event Streaming**: Real-time data updates

### Technology Upgrades

1. **GraphQL API**: Alternative to REST
2. **WebSocket Support**: Real-time updates
3. **Machine Learning**: Predictive analytics
4. **Data Lake**: Large-scale data storage

---

For implementation details, see:
- [Developer Guide](DEVELOPER_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT.md)

