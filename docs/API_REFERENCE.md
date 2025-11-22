# BI Platform API Reference

## Standardized Interface

All API Engine functions follow a standardized interface:
- **Input**: `dict` or `Path` objects
- **Output**: `dict` with standardized structure

## Core Classes

### StandardizedAPIEngine

Main entry point for all API operations.

```python
from api_engine.core.standardized_interface import StandardizedAPIEngine

engine = StandardizedAPIEngine()
```

## Methods

### send_email(params: Dict[str, Any]) -> Dict[str, Any]

Send an email via configured email provider.

**Input Parameters:**
```python
{
    "to": str,                    # Required: Recipient email
    "subject": str,               # Required: Email subject
    "content": str,               # Required: Email body (HTML or text)
    "from_email": Optional[str], # Optional: Sender email
    "cc": Optional[List[str]],   # Optional: CC recipients
    "bcc": Optional[List[str]],  # Optional: BCC recipients
    "attachments": Optional[List[Path]]  # Optional: File attachments
}
```

**Output:**
```python
{
    "status": "success" | "error",
    "message_id": str,
    "provider": str,              # e.g., "sendgrid", "mailgun"
    "error": Optional[str]        # Present if status == "error"
}
```

**Example:**
```python
result = engine.send_email({
    "to": "user@example.com",
    "subject": "Hello",
    "content": "<h1>Hello World</h1>"
})

if result["status"] == "success":
    print(f"Email sent: {result['message_id']}")
```

### upload_file(file_path: Union[Path, str], params: Dict[str, Any]) -> Dict[str, Any]

Upload a file to cloud storage.

**Input Parameters:**
- `file_path`: Path to file (Path object or string)
- `params`: Dictionary with:
  ```python
  {
      "bucket": str,              # Required: Storage bucket name
      "object_name": Optional[str] # Optional: Custom object name
  }
  ```

**Output:**
```python
{
    "status": "success" | "error",
    "url": str,                   # URL/path to uploaded file
    "bucket": str,
    "object_name": str,
    "error": Optional[str]
}
```

**Example:**
```python
result = engine.upload_file(
    Path("document.pdf"),
    {"bucket": "documents", "object_name": "contract.pdf"}
)
```

### create_envelope(document_path: Union[Path, str], params: Dict[str, Any]) -> Dict[str, Any]

Create an e-signature envelope.

**Input Parameters:**
- `document_path`: Path to document (Path object or string)
- `params`: Dictionary with:
  ```python
  {
      "signers": List[Dict[str, Any]],  # Required: List of signers
      # Each signer: {"email": str, "name": str, "role": Optional[str]}
      "subject": Optional[str]          # Optional: Envelope subject
  }
  ```

**Output:**
```python
{
    "status": "success" | "error",
    "envelope_id": str,
    "provider": str,              # e.g., "docusign"
    "error": Optional[str]
}
```

**Example:**
```python
result = engine.create_envelope(
    Path("contract.pdf"),
    {
        "signers": [
            {"email": "john@example.com", "name": "John Doe"},
            {"email": "jane@example.com", "name": "Jane Smith"}
        ],
        "subject": "Contract for Signature"
    }
)
```

### search(params: Dict[str, Any]) -> Dict[str, Any]

Perform a search query.

**Input Parameters:**
```python
{
    "query": str,                 # Required: Search query string
    "index": str,                # Required: Search index name
    "filters": Optional[Dict[str, Any]],  # Optional: Search filters
    "limit": Optional[int]       # Optional: Max results (default: 10)
}
```

**Output:**
```python
{
    "status": "success" | "error",
    "results": List[Dict[str, Any]],  # Search results
    "count": int,
    "error": Optional[str]
}
```

### send_letter(params: Dict[str, Any]) -> Dict[str, Any]

Send a physical letter via mail service.

**Input Parameters:**
```python
{
    "to_address": Dict[str, str],    # Required: Recipient address
    # {"name": str, "address_line1": str, "city": str, "state": str, "zip": str, "country": str}
    "from_address": Dict[str, str],  # Required: Sender address
    "content": str,                  # Required: Letter content (HTML)
    "color": Optional[bool]          # Optional: Print in color (default: False)
}
```

**Output:**
```python
{
    "status": "success" | "error",
    "letter_id": str,
    "provider": str,              # e.g., "lob"
    "error": Optional[str]
}
```

## Error Handling

All methods return a dictionary with a `status` field:
- `"success"`: Operation completed successfully
- `"error"`: Operation failed (check `error` field for details)

**Example Error Handling:**
```python
result = engine.send_email({...})

if result["status"] == "error":
    print(f"Error: {result['error']}")
    # Handle error
else:
    # Success
    print(f"Message ID: {result['message_id']}")
```

## Retry and Fallback

The API Engine automatically:
- Retries failed calls up to 3 times with exponential backoff
- Logs all API calls for audit purposes
- Supports fallback providers (configure in YAML)

## Configuration

Configure providers in `configs/dev/api_config.yaml` or via environment variables.

See `configs/dev/api_config.yaml` for examples.

## HTTP API

For HTTP-based integration, use the FastAPI service:

```bash
python -m api_engine.http_service
```

API documentation available at: `http://localhost:8000/docs`

