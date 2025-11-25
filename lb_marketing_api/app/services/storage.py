"""
Azure Blob Storage service for managing PDF files
"""
import logging
from typing import Optional
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
from ..config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for interacting with Azure Blob Storage"""
    
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        
        if not self.connection_string and not (self.account_name and self.account_key):
            logger.warning(
                "Azure Storage not configured. Either AZURE_STORAGE_CONNECTION_STRING "
                "or AZURE_STORAGE_ACCOUNT_NAME + AZURE_STORAGE_ACCOUNT_KEY must be set."
            )
            self.blob_service_client = None
        else:
            try:
                if self.connection_string:
                    self.blob_service_client = BlobServiceClient.from_connection_string(
                        self.connection_string
                    )
                else:
                    account_url = f"https://{self.account_name}.blob.core.windows.net"
                    self.blob_service_client = BlobServiceClient(
                        account_url=account_url,
                        credential=self.account_key
                    )
                # Ensure container exists
                self._ensure_container_exists()
            except Exception as e:
                logger.error(f"Failed to initialize Azure Storage client: {e}")
                self.blob_service_client = None
    
    def _ensure_container_exists(self):
        """Create container if it doesn't exist"""
        if not self.blob_service_client:
            return
        
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
        except Exception as e:
            logger.error(f"Failed to ensure container exists: {e}")
    
    def get_blob(self, blob_name: str) -> Optional[bytes]:
        """
        Download a blob from Azure Storage
        
        Args:
            blob_name: Name of the blob to download
            
        Returns:
            Blob content as bytes, or None if not found or error
        """
        if not self.blob_service_client:
            logger.error("Azure Storage client not initialized")
            return None
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            if not blob_client.exists():
                logger.warning(f"Blob not found: {blob_name}")
                return None
            
            # Get blob properties to check size
            blob_properties = blob_client.get_blob_properties()
            expected_size = blob_properties.size
            logger.info(f"Blob {blob_name} exists, expected size: {expected_size} bytes")
            
            download_stream = blob_client.download_blob()
            pdf_data = download_stream.readall()
            actual_size = len(pdf_data)
            
            logger.info(f"Downloaded {blob_name}: {actual_size} bytes (expected: {expected_size} bytes)")
            
            if actual_size != expected_size:
                logger.warning(
                    f"Size mismatch for {blob_name}: downloaded {actual_size} bytes, "
                    f"expected {expected_size} bytes"
                )
            
            return pdf_data
        except Exception as e:
            logger.error(f"Failed to download blob {blob_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def upload_blob(self, blob_name: str, data: bytes, content_type: str = "application/pdf") -> bool:
        """
        Upload a blob to Azure Storage
        
        Args:
            blob_name: Name of the blob
            data: Content to upload as bytes
            content_type: MIME type of the content
            
        Returns:
            True if successful, False otherwise
        """
        if not self.blob_service_client:
            logger.error("Azure Storage client not initialized")
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            content_settings = ContentSettings(content_type=content_type)
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=content_settings
            )
            logger.info(f"Successfully uploaded blob: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload blob {blob_name}: {e}")
            return False
    
    def blob_exists(self, blob_name: str) -> bool:
        """Check if a blob exists"""
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            return blob_client.exists()
        except Exception as e:
            logger.error(f"Failed to check blob existence {blob_name}: {e}")
            return False


# Global instance
storage_service = StorageService()

