# BI Platform - Complete API Documentation

Complete REST API documentation for the BI Platform API Engine.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [API Endpoints](#api-endpoints)
5. [Request/Response Formats](#requestresponse-formats)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Code Examples](#code-examples)
9. [SDK Usage](#sdk-usage)

## Overview

The BI Platform API Engine provides a unified REST API for integrating with various third-party services:

- **Email Services**: SendGrid, Mailgun
- **Storage Services**: AWS S3, Azure Blob Storage
- **E-Signature Services**: DocuSign
- **Search Services**: Elasticsearch
- **Physical Mail Services**: Lob.com

### API Version

- **Current Version**: v1.0.0
- **Base Path**: `/api/v1`

### Interactive Documentation

Once the API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Currently, the API uses configuration-based authentication. API keys are stored in configuration files or environment variables.

### Configuration

Set API keys in `.env` file or `configs/{environment}/api_config.yaml`:

```env
SENDGRID_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_key_here
DOCUSIGN_API_KEY=your_key_here
```

### Future Authentication

Future versions will support:
- API key authentication via headers
- OAuth 2.0
- JWT tokens

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

## API Endpoints

### 1. Root Endpoint

Get API information and available endpoints.

**Endpoint**: `GET /`

**Response**:
```json
{
  "name": "BI Platform API Engine",
  "version": "1.0.0",
  "endpoints": {
    "email": "/api/v1/email/send",
    "storage": "/api/v1/storage/upload",
    "signing": "/api/v1/signing/envelope",
    "search": "/api/v1/search",
    "physical_mail": "/api/v1/physical-mail/send"
  }
}
```

### 2. Health Check

Check API service health.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "api-engine"
}
```

### 3. Send Email

Send an email via configured email provider (SendGrid or Mailgun).

**Endpoint**: `POST /api/v1/email/send`

**Request Body**:
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "content": "<h1>Email Content</h1>",
  "from_email": "sender@example.com",
  "cc": ["cc1@example.com", "cc2@example.com"],
  "bcc": ["bcc@example.com"]
}
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | string | Yes | Recipient email address |
| `subject` | string | Yes | Email subject line |
| `content` | string | Yes | Email body (HTML or plain text) |
| `from_email` | string | No | Sender email address (uses default if not provided) |
| `cc` | array[string] | No | CC recipients |
| `bcc` | array[string] | No | BCC recipients |

**Response**:
```json
{
  "status": "success",
  "message_id": "msg_12345",
  "provider": "sendgrid"
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/v1/email/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Hello",
    "content": "<h1>Hello World</h1>"
  }'
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/email/send",
    json={
        "to": "recipient@example.com",
        "subject": "Hello",
        "content": "<h1>Hello World</h1>"
    }
)
print(response.json())
```

### 4. Upload File

Upload a file to cloud storage (AWS S3 or Azure Blob Storage).

**Endpoint**: `POST /api/v1/storage/upload`

**Request**: `multipart/form-data`

**Form Data**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | File to upload |
| `bucket` | string | No | Storage bucket/container name (default: "default") |
| `object_name` | string | No | Custom object name (default: original filename) |

**Response**:
```json
{
  "status": "success",
  "url": "https://bucket.s3.amazonaws.com/file.pdf",
  "bucket": "documents",
  "object_name": "file.pdf"
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/v1/storage/upload" \
  -F "file=@document.pdf" \
  -F "bucket=documents" \
  -F "object_name=my-document.pdf"
```

**Example (Python)**:
```python
import requests

with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "bucket": "documents",
        "object_name": "my-document.pdf"
    }
    response = requests.post(
        "http://localhost:8000/api/v1/storage/upload",
        files=files,
        data=data
    )
    print(response.json())
```

### 5. Create E-Signature Envelope

Create an e-signature envelope via DocuSign.

**Endpoint**: `POST /api/v1/signing/envelope`

**Request**: `multipart/form-data`

**Form Data**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document` | file | Yes | PDF document to sign |
| `signers` | string (JSON) | Yes | JSON array of signers |
| `subject` | string | No | Envelope subject |

**Signers Format**:
```json
[
  {
    "email": "signer1@example.com",
    "name": "John Doe"
  },
  {
    "email": "signer2@example.com",
    "name": "Jane Smith"
  }
]
```

**Response**:
```json
{
  "status": "success",
  "envelope_id": "abc123-def456",
  "provider": "docusign"
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/v1/signing/envelope" \
  -F "document=@contract.pdf" \
  -F 'signers=[{"email":"signer@example.com","name":"John Doe"}]' \
  -F "subject=Contract for Signature"
```

**Example (Python)**:
```python
import requests
import json

signers = [
    {"email": "signer@example.com", "name": "John Doe"}
]

with open("contract.pdf", "rb") as f:
    files = {"document": f}
    data = {
        "signers": json.dumps(signers),
        "subject": "Contract for Signature"
    }
    response = requests.post(
        "http://localhost:8000/api/v1/signing/envelope",
        files=files,
        data=data
    )
    print(response.json())
```

### 6. Search

Perform a search query using Elasticsearch.

**Endpoint**: `POST /api/v1/search`

**Request Body**:
```json
{
  "query": "search terms",
  "index": "documents",
  "filters": {
    "category": "contracts",
    "date_range": "2024-01-01,2024-12-31"
  },
  "limit": 10
}
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `index` | string | Yes | Search index name |
| `filters` | object | No | Additional filters |
| `limit` | integer | No | Maximum results (default: 10) |

**Response**:
```json
{
  "status": "success",
  "results": [
    {
      "id": "doc1",
      "title": "Document Title",
      "content": "Document content...",
      "score": 0.95
    }
  ],
  "count": 1
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract",
    "index": "documents",
    "limit": 10
  }'
```

### 7. Send Physical Letter

Send a physical letter via Lob.com.

**Endpoint**: `POST /api/v1/physical-mail/send`

**Request Body**:
```json
{
  "to_address": {
    "name": "John Doe",
    "address_line1": "123 Main St",
    "address_line2": "Apt 4",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "US"
  },
  "from_address": {
    "name": "Company Name",
    "address_line1": "456 Business Ave",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94102",
    "country": "US"
  },
  "content": "Letter content here...",
  "color": false
}
```

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to_address` | object | Yes | Recipient address |
| `from_address` | object | Yes | Sender address |
| `content` | string | Yes | Letter content |
| `color` | boolean | No | Print in color (default: false) |

**Response**:
```json
{
  "status": "success",
  "letter_id": "ltr_abc123",
  "provider": "lob"
}
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/physical-mail/send",
    json={
        "to_address": {
            "name": "John Doe",
            "address_line1": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "US"
        },
        "from_address": {
            "name": "Company Name",
            "address_line1": "456 Business Ave",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102",
            "country": "US"
        },
        "content": "Letter content here...",
        "color": False
    }
)
print(response.json())
```

## Request/Response Formats

### Content Types

- **JSON Requests**: `Content-Type: application/json`
- **File Uploads**: `Content-Type: multipart/form-data`

### Response Format

All responses follow this structure:

**Success Response**:
```json
{
  "status": "success",
  "data": { ... }
}
```

**Error Response**:
```json
{
  "detail": "Error message here"
}
```

## Error Handling

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 404 | Not Found - Endpoint doesn't exist |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**Missing Required Field**:
```json
{
  "detail": [
    {
      "loc": ["body", "to"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Invalid Email Format**:
```json
{
  "detail": "Invalid email address format"
}
```

**Provider Error**:
```json
{
  "detail": "Email sending failed: Provider API error"
}
```

## Rate Limiting

Currently, rate limiting is handled by individual providers. Future versions will include:

- Global rate limiting
- Per-API-key rate limits
- Rate limit headers in responses

## Code Examples

### Python SDK

```python
from api_engine.core.api_engine import APIEngine
from pathlib import Path

# Initialize engine
engine = APIEngine()

# Send email
result = engine.send_email(
    to="recipient@example.com",
    subject="Hello",
    content="<h1>Hello World</h1>"
)

# Upload file
url = engine.upload_file(
    Path("document.pdf"),
    bucket="documents"
)

# Create envelope
envelope_id = engine.create_envelope(
    document=Path("contract.pdf"),
    signers=[
        {"email": "signer@example.com", "name": "John Doe"}
    ]
)
```

### JavaScript/Node.js

```javascript
// Send email
const response = await fetch('http://localhost:8000/api/v1/email/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    to: 'recipient@example.com',
    subject: 'Hello',
    content: '<h1>Hello World</h1>'
  })
});

const data = await response.json();
console.log(data);
```

### cURL

```bash
# Send email
curl -X POST "http://localhost:8000/api/v1/email/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Hello",
    "content": "<h1>Hello World</h1>"
  }'

# Upload file
curl -X POST "http://localhost:8000/api/v1/storage/upload" \
  -F "file=@document.pdf" \
  -F "bucket=documents"
```

## SDK Usage

### Python SDK

The Python SDK is included in the package:

```python
from api_engine.core.api_engine import APIEngine

engine = APIEngine()

# All methods are available
engine.send_email(...)
engine.upload_file(...)
engine.create_envelope(...)
engine.search(...)
engine.send_letter(...)
```

See `examples/api_engine_usage.py` for complete examples.

## Testing

### Using Interactive Docs

1. Start the API: `python run_api.py`
2. Visit: http://localhost:8000/docs
3. Use Swagger UI to test endpoints interactively

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Test email endpoint
curl -X POST "http://localhost:8000/api/v1/email/send" \
  -H "Content-Type: application/json" \
  -d '{"to":"test@example.com","subject":"Test","content":"Test"}'
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Send email
response = requests.post(
    f"{BASE_URL}/api/v1/email/send",
    json={
        "to": "test@example.com",
        "subject": "Test",
        "content": "Test email"
    }
)
print(response.json())
```

## Best Practices

1. **Error Handling**: Always check response status codes
2. **Retries**: Implement retry logic for transient failures
3. **Validation**: Validate input data before sending requests
4. **Security**: Never expose API keys in client-side code
5. **Logging**: Log API calls for debugging and monitoring

## Future API Features

- API key authentication
- Webhook support
- Batch operations
- Rate limiting headers
- Request/response logging
- API versioning support

---

For more information, see:
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Integration Guide](docs/INTEGRATION_GUIDE.md)
- [Architecture Documentation](ARCHITECTURE.md)

