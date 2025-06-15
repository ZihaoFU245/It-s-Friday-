"""
Drive Skills Module

This module provides Google Drive-related functionality using the service layer.
All Drive operations use the drive service for better abstraction.
"""

from app import drive_service
from typing import Optional, Dict, Any


async def list_drive_files(
    max_results: int = 10,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """
    List files in Google Drive.
    
    Args:
        max_results: Maximum number of files to return
        query: Search query for filtering files
        
    Returns:
        Dict with Drive files information
    """
    return await drive_service.list_files(max_results, query)
