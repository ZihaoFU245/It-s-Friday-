"""
API endpoints and services
"""

from .config import Config

# Create a single Config instance for the entire application
config = Config()
# Note: Logging configuration is now handled by each entry point
# - FastAPI: configured in main.py
# - MCP Server: configured in skills/server.py

from .modules import FetchWeather, GmailClient, CalendarClient, DriveClient, ContactManager
from .services import WeatherService, EmailManager, CalendarService, DriveService

# Create service instances with shared config (lazy initialization inside services)
weather_service = WeatherService(config)
email_manager = EmailManager(config)  # Primary multi-account email service
calendar_service = CalendarService(config)
drive_service = DriveService(config)
ContactBooklet = ContactManager()

__all__ = [
    'config', 
    # Core modules (for advanced use)
    'FetchWeather', 'GmailClient', 'CalendarClient', 'DriveClient', 'ContactManager'
    # High-level services (recommended for most use cases)
    'weather_service', 'email_manager', 'calendar_service', 'drive_service', 'ContactBooklet'
]
