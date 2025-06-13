"""
API endpoints and services
"""

from .config import Config

# Create a single Config instance for the entire application
config = Config()
# Configure logging once at application startup
config.configure_logging()

from .modules import FetchWeather, GmailClient, CalendarClient, DriveClient
from .services import WeatherService, EmailService, CalendarService, DriveService

# Create service instances with shared config (lazy initialization inside services)
weather_service = WeatherService(config)
email_service = EmailService(config)
calendar_service = CalendarService(config)
drive_service = DriveService(config)

__all__ = [
    'config', 
    # Core modules (for advanced use)
    'FetchWeather', 'GmailClient', 'CalendarClient', 'DriveClient',
    # High-level services (recommended for most use cases)
    'weather_service', 'email_service', 'calendar_service', 'drive_service'
]
