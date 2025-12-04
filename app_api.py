"""
FastAPI HTTP service for BI Platform API Engine.

Provides REST endpoints for:
- Email sending (via MailService with provider switching)
- Data connectors (CSV, database, API)
- Provider/secrets management
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import os
from pathlib import Path

from api_engine.mail_service import MailService
from api_engine.core.config_manager import ConfigManager
from api_engine.secrets_manager import SecretsManager
from api_engine.providers.registry import default_registry
from bi_dashboard.core.data_connector import DataSourceManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BI Platform API Engine",
    description="Unified API for BI data connectors and third-party integrations",
    version="1.0.1"
)

# Initialize services
config_manager = ConfigManager()
mail_service = MailService(config_manager=config_manager)
secrets_manager = SecretsManager()
data_manager = DataSourceManager()


# ============================================================================
# Pydantic Models
# ============================================================================

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    content: str
    provider: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None


class SendEmailResponse(BaseModel):
    status: str
    message_id: Optional[str] = None
    provider: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    providers_registered: List[str]


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check and service info."""
    return HealthResponse(
        status="healthy",
        version="1.0.1",
        providers_registered=default_registry.list_providers()
    )


@app.get("/health", response_model=HealthResponse)
async def health_detailed():
    """Detailed health check."""
    return await health_check()


# ============================================================================
# Email Endpoints
# ============================================================================

@app.post("/email/send", response_model=SendEmailResponse)
async def send_email(request: SendEmailRequest):
    """
    Send an email using the configured provider.

    Args:
        to: Recipient email address
        subject: Email subject
        content: Email content (HTML supported)
        provider: Optional provider name (sendgrid, mailgun, etc.)
        cc: Optional CC recipients
        bcc: Optional BCC recipients

    Returns:
        SendEmailResponse with status and message ID
    """
    try:
        result = mail_service.send_email(
            to=request.to,
            subject=request.subject,
            content=request.content,
            provider=request.provider,
            cc=request.cc,
            bcc=request.bcc
        )
        return SendEmailResponse(
            status="success",
            message_id=result.get("message_id"),
            provider=result.get("provider")
        )
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@app.get("/email/providers")
async def list_email_providers():
    """List registered email providers."""
    providers = [p for p in default_registry.list_providers() if "mail" in p or "sendgrid" in p or "mailgun" in p]
    return {"available_providers": providers}


# ============================================================================
# Data Connector Endpoints
# ============================================================================

class DataSourceLoadRequest(BaseModel):
    source_name: str
    config: Optional[Dict[str, Any]] = None


class DataSourceLoadResponse(BaseModel):
    status: str
    rows: int
    columns: int
    column_names: List[str]
    error: Optional[str] = None


@app.post("/data/load", response_model=DataSourceLoadResponse)
async def load_data_source(request: DataSourceLoadRequest):
    """
    Load a data source by name from configuration.

    Args:
        source_name: Name of the data source (e.g., 'sales_csv', 'db_primary')
        config: Optional configuration dict; if not provided, uses configs/shared_config.yaml

    Returns:
        DataSourceLoadResponse with row/column counts and names
    """
    try:
        cfg = request.config or config_manager.get_dict() if hasattr(config_manager, 'get_dict') else {}
        df = data_manager.load_from_config(cfg, request.source_name)
        return DataSourceLoadResponse(
            status="success",
            rows=len(df),
            columns=len(df.columns),
            column_names=list(df.columns)
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Data source not found: {e}")
    except Exception as e:
        logger.error(f"Failed to load data source: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load data source: {str(e)}")


@app.post("/data/upload")
async def upload_data_file(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file and return metadata.

    Args:
        file: CSV or Excel file

    Returns:
        Metadata about the uploaded file
    """
    import pandas as pd
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(__import__('io').StringIO(contents.decode('utf-8')))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(__import__('io').BytesIO(contents))
        else:
            raise ValueError(f"Unsupported file type: {file.filename}")

        return {
            "status": "success",
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to upload file: {str(e)}")


# ============================================================================
# Configuration Endpoints
# ============================================================================

@app.get("/config/providers")
async def get_provider_config():
    """Get registered providers and their status."""
    return {
        "email_providers": [p for p in default_registry.list_providers() if "mail" in p.lower() or "sendgrid" in p.lower() or "mailgun" in p.lower()],
        "all_providers": default_registry.list_providers()
    }


@app.get("/config/settings")
async def get_settings():
    """Get current configuration settings."""
    return {
        "dashboard": config_manager.get("dashboard", {}),
        "api": config_manager.get("api", {}),
        "database": config_manager.get("database", {})
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("API_DEBUG", "false").lower() == "true"

    print("=" * 60)
    print("BI Platform API Engine - FastAPI Server")
    print("=" * 60)
    print(f"\nStarting server on {host}:{port}...")
    print(f"API documentation: http://{host}:{port}/docs")
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info" if debug else "warning"
    )
