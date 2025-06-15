"""
Calendar Skills Module

This module provides calendar-related functionality using the service layer.
All calendar operations use the calendar service for better abstraction.
"""

from app import calendar_service
from typing import Optional, Dict, Any


async def get_upcoming_events(
    max_results: int = 10,
    time_min: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get upcoming calendar events.
    
    Args:
        max_results: Maximum number of events to return
        time_min: Minimum time filter (ISO format)
        
    Returns:
        Dict with upcoming events information
    """
    return await calendar_service.get_upcoming_events(max_results, time_min)
