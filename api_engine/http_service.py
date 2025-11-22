"""
HTTP API service for API Engine using FastAPI.
Provides REST API endpoints for all API Engine functions.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from pathlib import Path
import uvicorn

from .core.api_engine import APIEngine
from .utils.logging import setup_logging, get_logger


# Setup logging
setup_logging()
logger = get_logger("HTTPService")

# Initialize FastAPI app
app = FastAPI(
    title="BI Platform API Engine",
    description="Unified API integration engine for third-party services",
    version="1.0.0",
    docs_url="/docs",  # Explicitly enable Swagger UI
    redoc_url="/redoc",  # Explicitly enable ReDoc
    openapi_url="/openapi.json"  # OpenAPI schema endpoint
)

# Initialize API Engine
api_engine = APIEngine()


# Request/Response Models
class EmailRequest(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    content: str = Field(..., description="Email content (HTML or plain text)")
    from_email: Optional[str] = Field(None, description="Sender email address")
    cc: Optional[List[str]] = Field(None, description="CC recipients")
    bcc: Optional[List[str]] = Field(None, description="BCC recipients")


class EmailResponse(BaseModel):
    status: str
    message_id: str
    provider: str


class StorageUploadRequest(BaseModel):
    bucket: str = Field(..., description="Storage bucket name")
    object_name: Optional[str] = Field(None, description="Optional object name")


class StorageUploadResponse(BaseModel):
    status: str
    url: str
    bucket: str
    object_name: str


class EnvelopeRequest(BaseModel):
    signers: List[Dict[str, Any]] = Field(..., description="List of signers")
    subject: Optional[str] = Field(None, description="Envelope subject")


class EnvelopeResponse(BaseModel):
    status: str
    envelope_id: str
    provider: str


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    index: str = Field(..., description="Search index name")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    limit: int = Field(10, description="Maximum results")


class LetterRequest(BaseModel):
    to_address: Dict[str, str] = Field(..., description="Recipient address")
    from_address: Dict[str, str] = Field(..., description="Sender address")
    content: str = Field(..., description="Letter content")
    color: bool = Field(False, description="Print in color")


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
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


@app.post("/api/v1/email/send", response_model=EmailResponse)
async def send_email(request: EmailRequest) -> EmailResponse:
    """Send an email via configured email provider."""
    try:
        result = api_engine.send_email(
            to=request.to,
            subject=request.subject,
            content=request.content,
            from_email=request.from_email,
            cc=request.cc,
            bcc=request.bcc
        )
        return EmailResponse(**result)
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/storage/upload", response_model=StorageUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    bucket: str = None,
    object_name: Optional[str] = None
) -> StorageUploadResponse:
    """Upload a file to cloud storage."""
    try:
        # Save uploaded file temporarily
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Upload to storage
        url = api_engine.upload_file(
            file_path=temp_path,
            bucket=bucket or "default",
            object_name=object_name
        )
        
        # Clean up temp file
        temp_path.unlink()
        
        return StorageUploadResponse(
            status="success",
            url=url,
            bucket=bucket or "default",
            object_name=object_name or file.filename
        )
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/signing/envelope", response_model=EnvelopeResponse)
async def create_envelope(
    document: UploadFile = File(...),
    signers: str = None,  # JSON string
    subject: Optional[str] = None
) -> EnvelopeResponse:
    """Create an e-signature envelope."""
    try:
        import json
        
        # Save document temporarily
        temp_path = Path(f"/tmp/{document.filename}")
        with open(temp_path, "wb") as f:
            content = await document.read()
            f.write(content)
        
        # Parse signers
        signers_list = json.loads(signers) if signers else []
        
        # Create envelope
        envelope_id = api_engine.create_envelope(
            document=temp_path,
            signers=signers_list,
            subject=subject
        )
        
        # Clean up
        temp_path.unlink()
        
        return EnvelopeResponse(
            status="success",
            envelope_id=envelope_id,
            provider="docusign"  # Get from config
        )
    except Exception as e:
        logger.error(f"Envelope creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/search")
async def search(request: SearchRequest) -> Dict[str, Any]:
    """Perform a search query."""
    try:
        results = api_engine.search(
            query=request.query,
            index=request.index,
            filters=request.filters,
            limit=request.limit
        )
        return {
            "status": "success",
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/physical-mail/send")
async def send_letter(request: LetterRequest) -> Dict[str, Any]:
    """Send a physical letter."""
    try:
        letter_id = api_engine.send_letter(
            to_address=request.to_address,
            from_address=request.from_address,
            content=request.content,
            color=request.color
        )
        return {
            "status": "success",
            "letter_id": letter_id,
            "provider": "lob"
        }
    except Exception as e:
        logger.error(f"Letter sending failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-engine"}


def main():
    """Run the HTTP server."""
    logger.info("Starting API Engine HTTP service...")
    logger.info("API Documentation available at:")
    logger.info("  - Swagger UI: http://localhost:8000/docs")
    logger.info("  - ReDoc: http://localhost:8000/redoc")
    logger.info("  - OpenAPI JSON: http://localhost:8000/openapi.json")
    uvicorn.run(
        app,  # Pass app directly instead of string
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

