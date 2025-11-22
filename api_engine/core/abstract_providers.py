"""
Abstract base classes for all provider implementations.
This module defines the interfaces that all providers must implement.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any


class EmailProvider(ABC):
    """Abstract base class for email service providers."""
    
    @abstractmethod
    def send_email(self, to: str, subject: str, content: str, 
                   from_email: Optional[str] = None, 
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   attachments: Optional[List[Path]] = None) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            content: Email body content (HTML or plain text)
            from_email: Sender email address
            cc: List of CC recipients
            bcc: List of BCC recipients
            attachments: List of file paths to attach
            
        Returns:
            Dictionary with response data including status and message_id
        """
        pass
    
    @abstractmethod
    def get_status(self, message_id: str) -> Dict[str, Any]:
        """Get the status of a sent email."""
        pass


class StorageProvider(ABC):
    """Abstract base class for cloud storage providers."""
    
    @abstractmethod
    def upload_file(self, file_path: Path, bucket: str, 
                   object_name: Optional[str] = None) -> str:
        """
        Upload a file to cloud storage.
        
        Args:
            file_path: Local path to the file
            bucket: Storage bucket/container name
            object_name: Optional custom object name
            
        Returns:
            URL or path to the uploaded file
        """
        pass
    
    @abstractmethod
    def download_file(self, object_name: str, bucket: str, 
                     local_path: Path) -> Path:
        """Download a file from cloud storage."""
        pass
    
    @abstractmethod
    def delete_file(self, object_name: str, bucket: str) -> bool:
        """Delete a file from cloud storage."""
        pass
    
    @abstractmethod
    def list_files(self, bucket: str, prefix: Optional[str] = None) -> List[str]:
        """List files in a bucket."""
        pass


class SigningProvider(ABC):
    """Abstract base class for e-signature service providers."""
    
    @abstractmethod
    def create_envelope(self, document: Path, signers: List[Dict[str, Any]], 
                       subject: Optional[str] = None) -> str:
        """
        Create an e-signature envelope.
        
        Args:
            document: Path to the document to sign
            signers: List of signer dictionaries with 'email', 'name', 'role'
            subject: Optional envelope subject
            
        Returns:
            Envelope ID
        """
        pass
    
    @abstractmethod
    def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Get the status of an envelope."""
        pass
    
    @abstractmethod
    def void_envelope(self, envelope_id: str, reason: str) -> bool:
        """Void an envelope."""
        pass


class SearchProvider(ABC):
    """Abstract base class for search service providers."""
    
    @abstractmethod
    def search(self, query: str, index: str, 
              filters: Optional[Dict[str, Any]] = None,
              limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a search query.
        
        Args:
            query: Search query string
            index: Search index name
            filters: Optional filters to apply
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    def index_document(self, document_id: str, document: Dict[str, Any], 
                      index: str) -> bool:
        """Index a document for search."""
        pass


class PhysicalMailProvider(ABC):
    """Abstract base class for physical mail service providers."""
    
    @abstractmethod
    def send_letter(self, to_address: Dict[str, str], 
                   from_address: Dict[str, str],
                   content: str, color: bool = False) -> str:
        """
        Send a physical letter.
        
        Args:
            to_address: Recipient address dictionary
            from_address: Sender address dictionary
            content: Letter content
            color: Whether to print in color
            
        Returns:
            Letter ID
        """
        pass
    
    @abstractmethod
    def get_letter_status(self, letter_id: str) -> Dict[str, Any]:
        """Get the status of a sent letter."""
        pass
