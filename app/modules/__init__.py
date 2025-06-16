"""
Modules for APIs
"""

from .weather import FetchWeather, Location
from .google_clients import (
    GmailClient,
    CalendarClient,
    DriveClient
)
from .contact_booklet import ContactManager