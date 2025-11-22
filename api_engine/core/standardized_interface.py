"""
Standardized interfaces for all API Engine functions.
All functions accept dict/Path inputs and return dict/Path outputs.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from .api_engine import APIEngine
from .retry_handler import RetryHandler, FallbackProvider
from .api_logger import APICallLogger, log_api_call


class StandardizedAPIEngine:
    """
    Standardized API Engine with dict/Path interfaces.
    All methods follow the pattern: input dict/Path -> output dict/Path
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize standardized API engine.
        
        Args:
            config_path: Optional path to config directory
        """
        self.engine = APIEngine(config_path)
        self.retry_handler = RetryHandler(max_retries=3, base_delay=1.0)
        self.logger = APICallLogger()
    
    def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email with standardized interface.
        
        Input dict:
            {
                "to": str,
                "subject": str,
                "content": str,
                "from_email": Optional[str],
                "cc": Optional[List[str]],
                "bcc": Optional[List[str]],
                "attachments": Optional[List[Path]]
            }
        
        Output dict:
            {
                "status": "success" | "error",
                "message_id": str,
                "provider": str,
                "error": Optional[str]
            }
        """
        try:
            result = self.retry_handler.retry(
                self.engine.send_email,
                params.get("to"),
                params.get("subject"),
                params.get("content"),
                from_email=params.get("from_email"),
                cc=params.get("cc"),
                bcc=params.get("bcc")
            )
            
            self.logger.log_call(
                provider=result.get("provider", "unknown"),
                method="send_email",
                request_params=params,
                response=result
            )
            
            return {
                "status": "success",
                **result
            }
        except Exception as e:
            self.logger.log_call(
                provider="unknown",
                method="send_email",
                request_params=params,
                error=str(e)
            )
            return {
                "status": "error",
                "error": str(e)
            }
    
    def upload_file(self, file_path: Union[Path, str], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload file with standardized interface.
        
        Input:
            file_path: Path to file (Path or str)
            params: {
                "bucket": str,
                "object_name": Optional[str]
            }
        
        Output dict:
            {
                "status": "success" | "error",
                "url": str,
                "bucket": str,
                "object_name": str,
                "error": Optional[str]
            }
        """
        try:
            file_path = Path(file_path) if isinstance(file_path, str) else file_path
            
            url = self.retry_handler.retry(
                self.engine.upload_file,
                file_path,
                params.get("bucket"),
                object_name=params.get("object_name")
            )
            
            self.logger.log_call(
                provider="storage",
                method="upload_file",
                request_params={"bucket": params.get("bucket"), "file": str(file_path)},
                response={"url": url}
            )
            
            return {
                "status": "success",
                "url": url,
                "bucket": params.get("bucket"),
                "object_name": params.get("object_name") or file_path.name
            }
        except Exception as e:
            self.logger.log_call(
                provider="storage",
                method="upload_file",
                request_params=params,
                error=str(e)
            )
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_envelope(self, document_path: Union[Path, str], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create e-signature envelope with standardized interface.
        
        Input:
            document_path: Path to document (Path or str)
            params: {
                "signers": List[Dict[str, Any]],  # [{"email": str, "name": str, "role": str}]
                "subject": Optional[str]
            }
        
        Output dict:
            {
                "status": "success" | "error",
                "envelope_id": str,
                "provider": str,
                "error": Optional[str]
            }
        """
        try:
            document_path = Path(document_path) if isinstance(document_path, str) else document_path
            
            envelope_id = self.retry_handler.retry(
                self.engine.create_envelope,
                document_path,
                params.get("signers", []),
                subject=params.get("subject")
            )
            
            self.logger.log_call(
                provider="signing",
                method="create_envelope",
                request_params={"document": str(document_path), "signers_count": len(params.get("signers", []))},
                response={"envelope_id": envelope_id}
            )
            
            return {
                "status": "success",
                "envelope_id": envelope_id,
                "provider": "docusign"  # Get from config
            }
        except Exception as e:
            self.logger.log_call(
                provider="signing",
                method="create_envelope",
                request_params=params,
                error=str(e)
            )
            return {
                "status": "error",
                "error": str(e)
            }
    
    def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search with standardized interface.
        
        Input dict:
            {
                "query": str,
                "index": str,
                "filters": Optional[Dict[str, Any]],
                "limit": Optional[int]
            }
        
        Output dict:
            {
                "status": "success" | "error",
                "results": List[Dict[str, Any]],
                "count": int,
                "error": Optional[str]
            }
        """
        try:
            results = self.retry_handler.retry(
                self.engine.search,
                params.get("query"),
                params.get("index"),
                filters=params.get("filters"),
                limit=params.get("limit", 10)
            )
            
            self.logger.log_call(
                provider="search",
                method="search",
                request_params=params,
                response={"count": len(results)}
            )
            
            return {
                "status": "success",
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            self.logger.log_call(
                provider="search",
                method="search",
                request_params=params,
                error=str(e)
            )
            return {
                "status": "error",
                "results": [],
                "count": 0,
                "error": str(e)
            }
    
    def send_letter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send physical letter with standardized interface.
        
        Input dict:
            {
                "to_address": Dict[str, str],  # {"name": str, "address_line1": str, ...}
                "from_address": Dict[str, str],
                "content": str,
                "color": Optional[bool]
            }
        
        Output dict:
            {
                "status": "success" | "error",
                "letter_id": str,
                "provider": str,
                "error": Optional[str]
            }
        """
        try:
            letter_id = self.retry_handler.retry(
                self.engine.send_letter,
                params.get("to_address"),
                params.get("from_address"),
                params.get("content"),
                color=params.get("color", False)
            )
            
            self.logger.log_call(
                provider="physical_mail",
                method="send_letter",
                request_params={"to": params.get("to_address", {}).get("name", "unknown")},
                response={"letter_id": letter_id}
            )
            
            return {
                "status": "success",
                "letter_id": letter_id,
                "provider": "lob"
            }
        except Exception as e:
            self.logger.log_call(
                provider="physical_mail",
                method="send_letter",
                request_params=params,
                error=str(e)
            )
            return {
                "status": "error",
                "error": str(e)
            }

