"""
Calendar Service - High-level calendar operations
"""

from typing import List, Dict, Any, Optional
import datetime
from ..modules.google_clients.calendar_client import CalendarClient


class CalendarService:
    """
    High-level calendar service that abstracts Google Calendar operations.
    """
    
    def __init__(self, config):
        self.config = config
        self._calendar_client = None
    
    @property
    def calendar_client(self) -> CalendarClient:
        """Lazy initialization of Calendar client"""
        if self._calendar_client is None:
            self._calendar_client = CalendarClient()
        return self._calendar_client
    
    def get_upcoming_events(
        self, 
        max_results: int = 10,
        time_min: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events.
        
        Args:
            max_results: Maximum number of events to return
            time_min: Start time for event search
            
        Returns:
            List of calendar events
        """
        try:
            return self.calendar_client.list_events(
                max_results=max_results,
                time_min=time_min
            )
        except Exception as e:
            return [{
                "error": str(e),
                "message": "Failed to fetch calendar events"
            }]
