"""
Skills Module - Standalone MCP Server

This module provides an MCP (Model Context Protocol) server that exposes
Friday's capabilities as tools for AI assistants to use.

The skills module is designed to be a standalone module that imports
services from the main app package, providing a clean separation of
concerns between the core application and the MCP interface.
"""

from skills.server import mcp
from skills.all_skills import (
    _get_weather_now,
    _get_weather_forecast,
    _get_weather_at,
    get_unread_emails,
    send_email,
    get_upcoming_events,
    list_drive_files
)

__all__ = [
    'mcp',
    'get_weather_now',
    'get_weather_forecast', 
    'get_unread_emails',
    'send_email',
    'get_upcoming_events',
    'list_drive_files'
]
