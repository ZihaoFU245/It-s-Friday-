"""
Drive Service - High-level Google Drive operations
"""

from typing import List, Dict, Any
from ..modules.google_clients.drive_client import DriveClient


class DriveService:
    """
    High-level drive service that abstracts Google Drive operations.
    """
    
    def __init__(self, config):
        self.config = config
        self._drive_client = None
    
    @property
    def drive_client(self) -> DriveClient:
        """Lazy initialization of Drive client"""
        if self._drive_client is None:
            self._drive_client = DriveClient()
        return self._drive_client
    
    def list_files(self, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        List files in Google Drive.
        
        Args:
            page_size: Number of files to return
            
        Returns:
            List of file information
        """
        try:
            return self.drive_client.list_files(page_size=page_size)
        except Exception as e:
            return [{
                "error": str(e),
                "message": "Failed to list Drive files"
            }]
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get information about a specific file.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            File metadata
        """
        try:
            return self.drive_client.get_file_metadata(file_id)
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to get info for file: {file_id}"
            }
