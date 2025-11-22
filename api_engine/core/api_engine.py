"""
Main API Engine class that orchestrates all providers.
"""
from typing import Dict, Any, Optional
from pathlib import Path

from .config_manager import ConfigManager
from .abstract_providers import (
    EmailProvider, StorageProvider, SigningProvider,
    SearchProvider, PhysicalMailProvider
)
from ..utils.logging import get_logger


class APIEngine:
    """Main API Engine that manages all providers."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the API Engine.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config = ConfigManager(config_dir)
        self.logger = get_logger("APIEngine")
        
        # Provider instances
        self.email_provider: Optional[EmailProvider] = None
        self.storage_provider: Optional[StorageProvider] = None
        self.signing_provider: Optional[SigningProvider] = None
        self.search_provider: Optional[SearchProvider] = None
        self.physical_mail_provider: Optional[PhysicalMailProvider] = None
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all providers based on configuration."""
        # Lazy import to avoid circular dependencies
        from ..providers.email_providers import (
            SendGridProvider, MailgunProvider
        )
        from ..providers.storage_providers import (
            S3Provider, AzureBlobProvider
        )
        from ..providers.signing_providers import (
            DocuSignProvider
        )
        from ..providers.search_providers import (
            ElasticsearchProvider
        )
        from ..providers.physical_mail_providers import (
            LobProvider
        )
        
        # Initialize email provider
        email_config = self.config.get_provider_config("email")
        email_type = email_config.get("type", "sendgrid")
        if email_type == "sendgrid":
            self.email_provider = SendGridProvider(email_config)
        elif email_type == "mailgun":
            self.email_provider = MailgunProvider(email_config)
        
        # Initialize storage provider
        storage_config = self.config.get_provider_config("storage")
        storage_type = storage_config.get("type", "s3")
        if storage_type == "s3":
            self.storage_provider = S3Provider(storage_config)
        elif storage_type == "azure":
            self.storage_provider = AzureBlobProvider(storage_config)
        
        # Initialize signing provider
        signing_config = self.config.get_provider_config("signing")
        signing_type = signing_config.get("type", "docusign")
        if signing_type == "docusign":
            self.signing_provider = DocuSignProvider(signing_config)
        
        # Initialize search provider
        search_config = self.config.get_provider_config("search")
        search_type = search_config.get("type", "elasticsearch")
        if search_type == "elasticsearch":
            self.search_provider = ElasticsearchProvider(search_config)
        
        # Initialize physical mail provider
        physical_mail_config = self.config.get_provider_config("physical_mail")
        physical_mail_type = physical_mail_config.get("type", "lob")
        if physical_mail_type == "lob":
            self.physical_mail_provider = LobProvider(physical_mail_config)
        
        self.logger.info("API Engine initialized with providers")
    
    def send_email(self, to: str, subject: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send an email using the configured email provider."""
        if not self.email_provider:
            raise ValueError("Email provider not configured")
        return self.email_provider.send_email(to, subject, content, **kwargs)
    
    def upload_file(self, file_path: Path, bucket: str, **kwargs) -> str:
        """Upload a file using the configured storage provider."""
        if not self.storage_provider:
            raise ValueError("Storage provider not configured")
        return self.storage_provider.upload_file(file_path, bucket, **kwargs)
    
    def create_envelope(self, document: Path, signers: list, **kwargs) -> str:
        """Create an e-signature envelope."""
        if not self.signing_provider:
            raise ValueError("Signing provider not configured")
        return self.signing_provider.create_envelope(document, signers, **kwargs)
    
    def search(self, query: str, index: str, **kwargs) -> list:
        """Perform a search query."""
        if not self.search_provider:
            raise ValueError("Search provider not configured")
        return self.search_provider.search(query, index, **kwargs)
    
    def send_letter(self, to_address: Dict[str, str], 
                   from_address: Dict[str, str], content: str, **kwargs) -> str:
        """Send a physical letter."""
        if not self.physical_mail_provider:
            raise ValueError("Physical mail provider not configured")
        return self.physical_mail_provider.send_letter(
            to_address, from_address, content, **kwargs
        )

