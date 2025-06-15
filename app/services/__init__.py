"""
Service Layer - Business Logic Abstraction

This layer provides high-level business operations that can be used by:
- FastAPI HTTP endpoints (main.py)
- MCP server (skills/server.py)
- CLI tools
- Future interfaces

Services abstract away module complexities and provide stable APIs
even when underlying modules change.
"""

from .weather_service import WeatherService
from .email_manager import EmailManager
from .calendar_service import CalendarService
from .drive_service import DriveService

__all__ = [
    'WeatherService',
    'EmailManager',
    'CalendarService',
    'DriveService'
]
