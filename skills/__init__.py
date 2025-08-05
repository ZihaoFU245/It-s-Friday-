"""
Skills Module - Standalone MCP Server

This module provides an MCP (Model Context Protocol) server that exposes
Friday's capabilities as tools for AI assistants to use.

The skills module is designed to be a standalone module that imports
services from the main app package, providing a clean separation of
concerns between the core application and the MCP interface.

The module is now organized into specific skill files:
- weather_skills.py: Weather-related operations
- email_skills.py: Email operations using EmailManager
- calendar_skills.py: Calendar operations
- drive_skills.py: Google Drive operations
- all_skills.py: Compatibility layer for existing imports
"""

from .server import mcp

# Import key functions for backward compatibility
from .weather_skills import (
        get_weather_now,
        get_weather_forecast,
        get_weather_at
    )
from .email_skills import (
        get_unread_emails,
        get_all_unread_emails,
        send_email,
        count_unread_emails,
        count_all_unread_emails,
        get_email_accounts,
        mark_emails_as_read,
        mark_emails_as_unread,
        delete_email,
        create_draft,
        update_draft,
        send_draft,
        list_drafts,
        get_draft,
        delete_draft
    )
from .calendar_skills import (
        get_upcoming_events
    )
from .drive_skills import (
        list_drive_files
    )

__all__ = [
    'mcp',
    # Weather functions
    '_get_weather_now',
    '_get_weather_forecast',
    '_get_weather_at',
    # Email functions
    'get_unread_emails',
    'get_all_unread_emails',
    'send_email',
    'count_unread_emails',
    'count_all_unread_emails',
    'get_email_accounts',
    'mark_emails_as_read',
    'mark_emails_as_unread',
    'delete_email',
    'create_draft',
    'update_draft',
    'send_draft',
    'list_drafts',
    'get_draft',
    'delete_draft',
    # Calendar functions
    'get_upcoming_events',
    # Drive functions
    'list_drive_files'
]
