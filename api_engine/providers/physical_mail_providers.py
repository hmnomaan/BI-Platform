"""
Physical mail service provider implementations.
"""
import requests
from typing import Dict, Any, Optional

from ..core.abstract_providers import PhysicalMailProvider
from ..utils.logging import get_logger


class LobProvider(PhysicalMailProvider):
    """Lob.com physical mail provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Lob provider.
        
        Args:
            config: Configuration dictionary with 'api_key' and optional 'api_version'
        """
        self.api_key = config.get("api_key")
        self.api_version = config.get("api_version", "2020-02-11")
        self.base_url = "https://api.lob.com/v1"
        self.logger = get_logger("LobProvider")
        
        if not self.api_key:
            raise ValueError("Lob API key required")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Basic {self.api_key}",
            "Lob-Version": self.api_version,
            "Content-Type": "application/json"
        }
    
    def send_letter(self, to_address: Dict[str, str],
                   from_address: Dict[str, str],
                   content: str, color: bool = False) -> str:
        """Send a physical letter via Lob."""
        url = f"{self.base_url}/letters"
        
        payload = {
            "to": {
                "name": to_address.get("name", ""),
                "address_line1": to_address.get("address_line1", ""),
                "address_line2": to_address.get("address_line2"),
                "address_city": to_address.get("city", ""),
                "address_state": to_address.get("state", ""),
                "address_zip": to_address.get("zip", ""),
                "address_country": to_address.get("country", "US")
            },
            "from": {
                "name": from_address.get("name", ""),
                "address_line1": from_address.get("address_line1", ""),
                "address_line2": from_address.get("address_line2"),
                "address_city": from_address.get("city", ""),
                "address_state": from_address.get("state", ""),
                "address_zip": from_address.get("zip", ""),
                "address_country": from_address.get("country", "US")
            },
            "file": content,  # In production, this should be a URL or file ID
            "color": color
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                auth=(self.api_key, "")
            )
            response.raise_for_status()
            
            result = response.json()
            letter_id = result.get("id")
            
            self.logger.info(f"Letter sent successfully: {letter_id}")
            return letter_id
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send letter via Lob: {e}")
            raise
    
    def get_letter_status(self, letter_id: str) -> Dict[str, Any]:
        """Get the status of a sent letter."""
        url = f"{self.base_url}/letters/{letter_id}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                auth=(self.api_key, "")
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "status": result.get("status"),
                "letter_id": letter_id,
                "expected_delivery_date": result.get("expected_delivery_date"),
                "date_created": result.get("date_created"),
                "provider": "lob"
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get letter status: {e}")
            return {"status": "error", "error": str(e)}

