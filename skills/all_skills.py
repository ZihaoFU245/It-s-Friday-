"""
Skills using the Service Layer

This module now uses the clean service layer instead of directly 
accessing modules. This provides better abstraction and stability.

The skills module imports services from the main app package to
access weather, email, calendar, and drive functionality.
"""

# Import services from the main app package
from app import weather_service, email_service, calendar_service, drive_service
from typing import Optional, Union, Tuple, Dict, Any

# Weather operations using service layer
async def fetch_weather(
    city: Optional[str] = None, 
    type_: str = "current"
) -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
    """
    Fetch weather using the weather service.
    Now provider-agnostic and with better error handling.
    """
    return await weather_service.get_weather(city=city, mode=type_)

async def get_weather_forecast(
    city: Optional[str] = None
) -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
    """Get weather forecast using service layer"""
    return await weather_service.get_forecast(city=city)

# Email operations using service layer  
def get_unread_emails(max_results: int = 10):
    """Get unread emails using service layer"""
    return email_service.get_unread_messages(max_results=max_results)

def send_email(to: str, subject: str, body: str, html_body: Optional[str] = None):
    """Send email using service layer"""
    return email_service.send_email(to=to, subject=subject, body=body, html_body=html_body)

# Calendar operations using service layer
def get_upcoming_events(max_results: int = 10):
    """Get upcoming calendar events using service layer"""
    return calendar_service.get_upcoming_events(max_results=max_results)

# Drive operations using service layer
def list_drive_files(page_size: int = 10):
    """List Google Drive files using service layer"""
    return drive_service.list_files(page_size=page_size)
