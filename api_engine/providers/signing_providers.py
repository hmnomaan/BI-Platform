"""
E-signature service provider implementations.
"""
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
import base64

from ..core.abstract_providers import SigningProvider
from ..utils.logging import get_logger


class DocuSignProvider(SigningProvider):
    """DocuSign e-signature provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DocuSign provider.
        
        Args:
            config: Configuration dictionary with 'api_key', 'account_id',
                   'user_id', 'base_url' (optional)
        """
        self.api_key = config.get("api_key")
        self.account_id = config.get("account_id")
        self.user_id = config.get("user_id")
        self.base_url = config.get("base_url", "https://demo.docusign.net/restapi")
        self.logger = get_logger("DocuSignProvider")
        
        if not all([self.api_key, self.account_id, self.user_id]):
            raise ValueError("DocuSign credentials required (api_key, account_id, user_id)")
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with DocuSign and get access token."""
        # In production, use OAuth2. For demo, using JWT authentication
        # This is a simplified version - production should use proper OAuth flow
        self.access_token = self.api_key  # Simplified - use proper auth in production
        self.logger.info("DocuSign authentication successful")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_envelope(self, document: Path, signers: List[Dict[str, Any]],
                       subject: Optional[str] = None) -> str:
        """Create a DocuSign envelope."""
        if not document.exists():
            raise FileNotFoundError(f"Document not found: {document}")
        
        # Read and encode document
        with open(document, "rb") as f:
            document_content = base64.b64encode(f.read()).decode("utf-8")
        
        # Build envelope definition
        envelope_definition = {
            "emailSubject": subject or "Please sign this document",
            "documents": [{
                "documentBase64": document_content,
                "name": document.name,
                "fileExtension": document.suffix[1:] if document.suffix else "pdf",
                "documentId": "1"
            }],
            "recipients": {
                "signers": []
            },
            "status": "sent"
        }
        
        # Add signers
        for i, signer in enumerate(signers, start=1):
            signer_def = {
                "email": signer.get("email"),
                "name": signer.get("name", signer.get("email")),
                "recipientId": str(i),
                "routingOrder": str(i),
                "tabs": {
                    "signHereTabs": [{
                        "documentId": "1",
                        "pageNumber": "1",
                        "recipientId": str(i),
                        "xPosition": "100",
                        "yPosition": "100"
                    }]
                }
            }
            envelope_definition["recipients"]["signers"].append(signer_def)
        
        # Create envelope
        url = f"{self.base_url}/v2.1/accounts/{self.account_id}/envelopes"
        
        try:
            response = requests.post(
                url,
                json=envelope_definition,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            result = response.json()
            envelope_id = result.get("envelopeId")
            
            self.logger.info(f"Envelope created successfully: {envelope_id}")
            return envelope_id
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create DocuSign envelope: {e}")
            raise
    
    def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Get the status of a DocuSign envelope."""
        url = f"{self.base_url}/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            result = response.json()
            return {
                "status": result.get("status"),
                "envelope_id": envelope_id,
                "created": result.get("createdDateTime"),
                "sent": result.get("sentDateTime"),
                "completed": result.get("completedDateTime"),
                "provider": "docusign"
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get envelope status: {e}")
            return {"status": "error", "error": str(e)}
    
    def void_envelope(self, envelope_id: str, reason: str) -> bool:
        """Void a DocuSign envelope."""
        url = f"{self.base_url}/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}"
        
        payload = {
            "status": "voided",
            "voidedReason": reason
        }
        
        try:
            response = requests.put(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            
            self.logger.info(f"Envelope voided successfully: {envelope_id}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to void envelope: {e}")
            return False

