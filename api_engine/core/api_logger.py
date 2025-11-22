"""
API call logging for audit and traceability.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import time

from ..utils.logging import get_logger


logger = get_logger("APILogger")


class APICallLogger:
    """Logs all API calls with detailed information."""
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize API logger.
        
        Args:
            log_file: Path to JSONL log file (default: logs/api_call_logs.jsonl)
        """
        if log_file is None:
            log_file = Path("logs") / "api_call_logs.jsonl"
        
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_call(self, provider: str, method: str, request_params: Dict[str, Any],
                 response: Optional[Dict[str, Any]] = None, error: Optional[str] = None,
                 duration_ms: Optional[float] = None):
        """
        Log an API call.
        
        Args:
            provider: Service provider name (e.g., "sendgrid", "s3")
            method: Method name (e.g., "send_email", "upload_file")
            request_params: Request parameters (sensitive data should be masked)
            response: Response data
            error: Error message if call failed
            duration_ms: Call duration in milliseconds
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider,
            "method": method,
            "request": self._mask_sensitive_data(request_params),
            "response": response,
            "error": error,
            "duration_ms": duration_ms,
            "status": "success" if error is None else "error"
        }
        
        # Write to JSONL file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # Also log to standard logger
        if error:
            logger.error(f"API call failed: {provider}.{method} - {error}")
        else:
            logger.info(f"API call: {provider}.{method} - {duration_ms:.2f}ms")
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields in request parameters."""
        sensitive_keys = ["password", "api_key", "secret", "token", "key"]
        masked = data.copy()
        
        for key, value in masked.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(value, str) and len(value) > 4:
                    masked[key] = "*" * (len(value) - 4) + value[-4:]
                else:
                    masked[key] = "***"
        
        return masked
    
    def get_calls(self, provider: Optional[str] = None,
                 method: Optional[str] = None,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Retrieve logged API calls with filters.
        
        Args:
            provider: Filter by provider
            method: Filter by method
            start_date: Filter by start date
            end_date: Filter by end date
        
        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []
        
        entries = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    
                    # Apply filters
                    if provider and entry.get("provider") != provider:
                        continue
                    if method and entry.get("method") != method:
                        continue
                    
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if start_date and entry_time < start_date:
                        continue
                    if end_date and entry_time > end_date:
                        continue
                    
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return entries
    
    def get_statistics(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get API call statistics.
        
        Args:
            provider: Filter by provider
        
        Returns:
            Statistics dictionary
        """
        calls = self.get_calls(provider=provider)
        
        if not calls:
            return {
                "total_calls": 0,
                "success_count": 0,
                "error_count": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0
            }
        
        success_count = sum(1 for c in calls if c.get("status") == "success")
        error_count = len(calls) - success_count
        durations = [c.get("duration_ms", 0) for c in calls if c.get("duration_ms")]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        return {
            "total_calls": len(calls),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / len(calls) if calls else 0.0,
            "avg_duration_ms": avg_duration,
            "providers": list(set(c.get("provider") for c in calls))
        }


def log_api_call(provider: str, method: str):
    """
    Decorator to automatically log API calls.
    
    Args:
        provider: Service provider name
        method: Method name
    """
    def decorator(func):
        logger_instance = APICallLogger()
        
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            response = None
            
            try:
                # Extract request params (mask sensitive data)
                request_params = kwargs.copy()
                for i, arg in enumerate(args):
                    request_params[f"arg_{i}"] = str(arg)[:100]  # Limit length
                
                result = func(*args, **kwargs)
                response = result if isinstance(result, dict) else {"result": "success"}
                
                duration_ms = (time.time() - start_time) * 1000
                
                logger_instance.log_call(
                    provider=provider,
                    method=method,
                    request_params=request_params,
                    response=response,
                    duration_ms=duration_ms
                )
                
                return result
            except Exception as e:
                error = str(e)
                duration_ms = (time.time() - start_time) * 1000
                
                logger_instance.log_call(
                    provider=provider,
                    method=method,
                    request_params=kwargs,
                    error=error,
                    duration_ms=duration_ms
                )
                
                raise
        
        return wrapper
    return decorator

