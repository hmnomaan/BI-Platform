"""
Cloud storage provider implementations.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..core.abstract_providers import StorageProvider
from ..utils.logging import get_logger


class S3Provider(StorageProvider):
    """AWS S3 storage provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize S3 provider.
        
        Args:
            config: Configuration dictionary with 'access_key_id', 'secret_access_key',
                   'region', and optional 'endpoint_url'
        """
        self.access_key_id = config.get("access_key_id")
        self.secret_access_key = config.get("secret_access_key")
        self.region = config.get("region", "us-east-1")
        self.endpoint_url = config.get("endpoint_url")
        
        self.logger = get_logger("S3Provider")
        
        # Initialize S3 client
        client_kwargs = {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "region_name": self.region
        }
        
        if self.endpoint_url:
            client_kwargs["endpoint_url"] = self.endpoint_url
        
        self.s3_client = boto3.client("s3", **client_kwargs)
    
    def upload_file(self, file_path: Path, bucket: str,
                   object_name: Optional[str] = None) -> str:
        """Upload a file to S3."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if object_name is None:
            object_name = file_path.name
        
        try:
            self.s3_client.upload_file(str(file_path), bucket, object_name)
            url = f"s3://{bucket}/{object_name}"
            
            self.logger.info(f"File uploaded successfully: {url}")
            return url
        except ClientError as e:
            self.logger.error(f"Failed to upload file to S3: {e}")
            raise
    
    def download_file(self, object_name: str, bucket: str,
                     local_path: Path) -> Path:
        """Download a file from S3."""
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.s3_client.download_file(bucket, object_name, str(local_path))
            self.logger.info(f"File downloaded successfully: {local_path}")
            return local_path
        except ClientError as e:
            self.logger.error(f"Failed to download file from S3: {e}")
            raise
    
    def delete_file(self, object_name: str, bucket: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=object_name)
            self.logger.info(f"File deleted successfully: s3://{bucket}/{object_name}")
            return True
        except ClientError as e:
            self.logger.error(f"Failed to delete file from S3: {e}")
            return False
    
    def list_files(self, bucket: str, prefix: Optional[str] = None) -> List[str]:
        """List files in an S3 bucket."""
        try:
            kwargs = {"Bucket": bucket}
            if prefix:
                kwargs["Prefix"] = prefix
            
            response = self.s3_client.list_objects_v2(**kwargs)
            files = [obj["Key"] for obj in response.get("Contents", [])]
            
            return files
        except ClientError as e:
            self.logger.error(f"Failed to list files in S3: {e}")
            return []


class AzureBlobProvider(StorageProvider):
    """Azure Blob Storage provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Azure Blob provider.
        
        Args:
            config: Configuration dictionary with 'connection_string' or
                   'account_name' and 'account_key'
        """
        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError:
            raise ImportError("azure-storage-blob package required for Azure provider")
        
        connection_string = config.get("connection_string")
        account_name = config.get("account_name")
        account_key = config.get("account_key")
        
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        elif account_name and account_key:
            account_url = f"https://{account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=account_key
            )
        else:
            raise ValueError("Azure storage credentials required")
        
        self.logger = get_logger("AzureBlobProvider")
    
    def upload_file(self, file_path: Path, bucket: str,
                   object_name: Optional[str] = None) -> str:
        """Upload a file to Azure Blob Storage."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if object_name is None:
            object_name = file_path.name
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=bucket, blob=object_name
            )
            
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            url = blob_client.url
            self.logger.info(f"File uploaded successfully: {url}")
            return url
        except Exception as e:
            self.logger.error(f"Failed to upload file to Azure: {e}")
            raise
    
    def download_file(self, object_name: str, bucket: str,
                     local_path: Path) -> Path:
        """Download a file from Azure Blob Storage."""
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=bucket, blob=object_name
            )
            
            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            self.logger.info(f"File downloaded successfully: {local_path}")
            return local_path
        except Exception as e:
            self.logger.error(f"Failed to download file from Azure: {e}")
            raise
    
    def delete_file(self, object_name: str, bucket: str) -> bool:
        """Delete a file from Azure Blob Storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=bucket, blob=object_name
            )
            blob_client.delete_blob()
            
            self.logger.info(f"File deleted successfully: {bucket}/{object_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file from Azure: {e}")
            return False
    
    def list_files(self, bucket: str, prefix: Optional[str] = None) -> List[str]:
        """List files in an Azure Blob container."""
        try:
            container_client = self.blob_service_client.get_container_client(bucket)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            files = [blob.name for blob in blobs]
            return files
        except Exception as e:
            self.logger.error(f"Failed to list files in Azure: {e}")
            return []

