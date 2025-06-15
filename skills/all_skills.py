"""
All Skills Module - Compatibility Layer

This module provides backward compatibility by importing from the refactored
skill modules. New code should import directly from the specific skill modules:
- weather_skills
- email_skills  
- calendar_skills
- drive_skills

This compatibility layer will be maintained to avoid breaking existing imports.
"""

# Import from refactored skill modules
from .weather_skills import (
    get_weather_now as _get_weather_now,
    get_weather_forecast as _get_weather_forecast,
    get_weather_at as _get_weather_at
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


