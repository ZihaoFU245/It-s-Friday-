"""
Email Clients Module

This module provides standardized email client implementations for different providers.
All clients implement the BaseEmailClient interface for consistent usage.

Client management is now handled by the EmailAccountManager in utils.py
"""

from .base_email_client import BaseEmailClient
from .gmail_client_adapter import GmailClientAdapter
# from .outlook_client_adapter import OutlookClientAdapter  # Uncomment when fully implemented

__all__ = [
    'BaseEmailClient',
    'GmailClientAdapter'
]
