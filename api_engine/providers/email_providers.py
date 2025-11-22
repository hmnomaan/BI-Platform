"""
Email service provider implementations.
"""
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..core.abstract_providers import EmailProvider
from ..utils.logging import get_logger


class SendGridProvider(EmailProvider):
    """SendGrid email provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SendGrid provider.
        
        Args:
            config: Configuration dictionary with 'api_key' and optional 'from_email'
        """
        self.api_key = config.get("api_key")
        self.from_email = config.get("from_email", "noreply@example.com")
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
        self.logger = get_logger("SendGridProvider")
        
        if not self.api_key:
            raise ValueError("SendGrid API key not provided")
    
    def send_email(self, to: str, subject: str, content: str,
                   from_email: Optional[str] = None,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   attachments: Optional[List[Path]] = None) -> Dict[str, Any]:
        """Send an email via SendGrid."""
        from_email = from_email or self.from_email
        
        payload = {
            "personalizations": [{
                "to": [{"email": to}],
            }],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{
                "type": "text/html",
                "value": content
            }]
        }
        
        if cc:
            payload["personalizations"][0]["cc"] = [{"email": email} for email in cc]
        if bcc:
            payload["personalizations"][0]["bcc"] = [{"email": email} for email in bcc]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            # SendGrid returns 202 Accepted with no body on success
            message_id = response.headers.get("X-Message-Id", "unknown")
            
            self.logger.info(f"Email sent successfully to {to}, message_id: {message_id}")
            
            return {
                "status": "success",
                "message_id": message_id,
                "provider": "sendgrid"
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send email via SendGrid: {e}")
            raise
    
    def get_status(self, message_id: str) -> Dict[str, Any]:
        """Get email status from SendGrid."""
        # SendGrid doesn't provide a simple status endpoint
        # This would require webhook setup or activity API
        return {
            "status": "unknown",
            "message": "Status retrieval requires webhook configuration"
        }


class MailgunProvider(EmailProvider):
    """Mailgun email provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Mailgun provider.
        
        Args:
            config: Configuration dictionary with 'api_key', 'domain', and optional 'from_email'
        """
        self.api_key = config.get("api_key")
        self.domain = config.get("domain")
        self.from_email = config.get("from_email", f"noreply@{self.domain}")
        self.api_url = f"https://api.mailgun.net/v3/{self.domain}/messages"
        self.logger = get_logger("MailgunProvider")
        
        if not self.api_key or not self.domain:
            raise ValueError("Mailgun API key and domain required")
    
    def send_email(self, to: str, subject: str, content: str,
                   from_email: Optional[str] = None,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   attachments: Optional[List[Path]] = None) -> Dict[str, Any]:
        """Send an email via Mailgun."""
        from_email = from_email or self.from_email
        
        data = {
            "from": from_email,
            "to": to,
            "subject": subject,
            "html": content
        }
        
        if cc:
            data["cc"] = ",".join(cc)
        if bcc:
            data["bcc"] = ",".join(bcc)
        
        files = []
        if attachments:
            for att_path in attachments:
                files.append(("attachment", open(att_path, "rb")))
        
        try:
            response = requests.post(
                self.api_url,
                auth=("api", self.api_key),
                data=data,
                files=files if files else None
            )
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get("id", "unknown")
            
            self.logger.info(f"Email sent successfully to {to}, message_id: {message_id}")
            
            return {
                "status": "success",
                "message_id": message_id,
                "provider": "mailgun"
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send email via Mailgun: {e}")
            raise
        finally:
            # Close file handles
            for _, file_obj in files:
                if hasattr(file_obj, 'close'):
                    file_obj.close()
    
    def get_status(self, message_id: str) -> Dict[str, Any]:
        """Get email status from Mailgun."""
        try:
            response = requests.get(
                f"https://api.mailgun.net/v3/{self.domain}/events",
                auth=("api", self.api_key),
                params={"message-id": message_id}
            )
            response.raise_for_status()
            events = response.json().get("items", [])
            
            if events:
                latest_event = events[0]
                return {
                    "status": latest_event.get("event", "unknown"),
                    "timestamp": latest_event.get("timestamp"),
                    "provider": "mailgun"
                }
            return {"status": "not_found", "provider": "mailgun"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get email status: {e}")
            return {"status": "error", "error": str(e)}
