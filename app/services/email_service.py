"""
Email Service - High-level email operations

⚠️ DEPRECATION NOTICE:
This single-account EmailService is now deprecated in favor of the multi-account EmailManager.
For new development, please use:
- EmailManager from app.services.email_manager for multi-account support
- EmailService is still available for backward compatibility

MIGRATION GUIDE:
Old: from app import email_service
New: from app import email_manager

Old: email_service.send_email(...)
New: email_manager.send_email(..., account="personal")

This service provides a unified interface for email operations across different providers.
It uses the BaseEmailClient abstraction to support Gmail, Outlook, and other email services
without requiring code changes when switching providers.

Features:
- Provider-agnostic email operations
- Automatic provider detection and initialization
- Consistent API across all email providers
- Support for multiple email accounts/providers simultaneously
- Comprehensive error handling and logging
- Async and sync operation support
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from ..modules.email_clients import BaseEmailClient, create_email_client, get_supported_providers
from ..config import Config


class EmailProvider(Enum):
    """Supported email providers."""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    EXCHANGE = "exchange"
    IMAP = "imap"


class EmailService:
    """
    High-level email service that provides a unified interface for email operations.
    
    This service abstracts the complexities of different email providers and provides
    a consistent API that works with Gmail, Outlook, Exchange, and other email services.
    
    Features:
    - Multi-provider support (Gmail, Outlook, Exchange, IMAP)
    - Automatic provider selection and initialization
    - Consistent API across all providers
    - Async and sync operation support
    - Comprehensive error handling
    - Message formatting and filtering
    - Advanced search capabilities
    - Draft management
    - Attachment handling
    - Folder/label management
    
    Usage:
        # Initialize with default provider (Gmail)
        email_service = EmailService(config)
        
        # Initialize with specific provider
        email_service = EmailService(config, provider="outlook")
        
        # Send email
        result = await email_service.send_email(
            to="recipient@example.com",
            subject="Test",
            body="Hello!"
        )
        
        # Get unread messages
        messages = email_service.get_unread_messages(max_results=10)
        """
    
    def __init__(self, config: Config, provider: str = "gmail"):
        """
        Initialize the email service.
        
        Args:
            config: Configuration object containing email settings
            provider: Email provider name (default: "gmail")
            
        Raises:
            ValueError: If provider is not supported
        """
        self.config = config
        self.provider_name = provider.lower()
        self.logger = logging.getLogger(__name__)
        
        # Validate provider
        if self.provider_name not in get_supported_providers():
            available = ', '.join(get_supported_providers())
            raise ValueError(f"Unsupported email provider: {provider}. Available: {available}")
        
        # Lazy initialization of email client
        self._email_client: Optional[BaseEmailClient] = None
        
        # Cache for provider capabilities
        self._capabilities_cache = {}
    
    @property
    def email_client(self) -> BaseEmailClient:
        """
        Lazy initialization of email client.
        
        Returns:
            BaseEmailClient implementation for the configured provider
        """
        if self._email_client is None:
            try:
                self._email_client = create_email_client(
                    self.provider_name,
                    config=self.config
                )
                self.logger.info(f"Initialized {self.provider_name} email client")
            except Exception as e:
                self.logger.error(f"Failed to initialize {self.provider_name} client: {e}")
                raise
        
        return self._email_client    
    # ========================================
    # PROVIDER INFORMATION METHODS
    # ========================================
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current email provider.
        
        Returns:
            Dict containing provider information and capabilities
        """
        try:
            profile = self.email_client.get_profile()
            
            return {
                'provider': self.provider_name,
                'email_address': profile.get('email_address'),
                'display_name': profile.get('display_name'),
                'account_type': profile.get('account_type'),
                'total_messages': profile.get('total_messages', 0),
                'capabilities': self.get_provider_capabilities(),
                'profile': profile
            }
        except Exception as e:
            self.logger.error(f"Failed to get provider info: {e}")
            return {
                'provider': self.provider_name,
                'error': str(e),
                'capabilities': {}
            }
    
    def get_provider_capabilities(self) -> Dict[str, bool]:
        """
        Get capabilities of the current email provider.
        
        Returns:
            Dict mapping capability names to support status
        """
        if not self._capabilities_cache:
            common_features = [
                'html_email', 'attachments', 'threading', 'labels', 
                'folders', 'search', 'drafts', 'advanced_search'
            ]
            
            self._capabilities_cache = {
                feature: self.email_client.supports_feature(feature)
                for feature in common_features
                }
        
        return self._capabilities_cache.copy()
    
    def switch_provider(self, new_provider: str, config: Optional[Config] = None):
        """
        Switch to a different email provider.
        
        Args:
            new_provider: New provider name
            config: Optional new configuration (uses existing config if not provided)
            
        Raises:
            ValueError: If provider is not supported
        """
        if new_provider.lower() not in get_supported_providers():
            available = ', '.join(get_supported_providers())
            raise ValueError(f"Unsupported email provider: {new_provider}. Available: {available}")
        
        self.provider_name = new_provider.lower()
        self.config = config or self.config
        self._email_client = None  # Force re-initialization
        self._capabilities_cache = {}  # Clear capabilities cache
        
        self.logger.info(f"Switched to {self.provider_name} email provider")
    
    # ========================================
    # EMAIL SENDING METHODS
    # ========================================
    
    async def send_email(
        self, 
        to: Union[str, List[str]], 
        subject: str, 
        body: str, 
        cc: Union[str, List[str]] = None,
        bcc: Union[str, List[str]] = None,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        validate_recipients: bool = True
    ) -> Dict[str, Any]:
        """
        Send an email with optional HTML body and attachments.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: Optional HTML body
            attachments: Optional list of file paths to attach
            validate_recipients: Whether to validate email addresses
            
        Returns:
            Dict with success status, message ID, and provider info
        """
        try:
            # Validate recipients if requested
            if validate_recipients:
                validation_result = self._validate_email_addresses(to, cc, bcc)
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'error': f"Invalid email addresses: {validation_result['invalid_addresses']}",
                        'provider': self.provider_name
                    }
            
            # Check if HTML is supported if html_body provided
            if html_body and not self.email_client.supports_feature('html_email'):
                self.logger.warning(f"{self.provider_name} doesn't support HTML emails, sending plain text only")
                html_body = None
            
            # Check if attachments are supported
            if attachments and not self.email_client.supports_feature('attachments'):
                self.logger.warning(f"{self.provider_name} doesn't support attachments, ignoring")
                attachments = None
            
            # Send the email
            result = self.email_client.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                html_body=html_body,
                attachments=attachments
            )
            
            # Add service-level metadata
            if result.get('success', True):
                result.update({
                    'service': 'EmailService',
                    'provider': self.provider_name,
                    'timestamp': self._get_current_timestamp(),
                    'features_used': {
                        'html': html_body is not None,
                        'attachments': bool(attachments),
                        'cc': cc is not None,
                        'bcc': bcc is not None
                    }
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send email via {self.provider_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    def send_email_sync(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Synchronous version of send_email.
        
        Args:
            Same as send_email
            
        Returns:
            Same as send_email
        """
        return asyncio.run(self.send_email(*args, **kwargs))
    
    async def reply_to_email(
        self,
        message_id: str,
        body: str,
        html_body: Optional[str] = None,
        reply_all: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Reply to an existing email message.
        
        Args:
            message_id: ID of the message to reply to
            body: Reply body text
            html_body: Reply HTML body (optional)
            reply_all: Whether to reply to all recipients
            attachments: List of file paths to attach (optional)
            
        Returns:
            Dict with success status and reply information
        """
        try:
            result = self.email_client.reply_to_message(
                message_id=message_id,
                body=body,
                html_body=html_body,
                reply_all=reply_all,
                attachments=attachments
            )
            
            # Add service-level metadata
            if result.get('success', True):
                result.update({
                    'service': 'EmailService',
                    'provider': self.provider_name,
                    'timestamp': self._get_current_timestamp(),
                    'reply_type': 'reply_all' if reply_all else 'reply'
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to reply to email {message_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    # ========================================
    # EMAIL RETRIEVAL METHODS
    # ========================================
    
    def get_unread_messages(
        self, 
        max_results: int = 10,
        folder: Optional[str] = None,
        hours_back: Optional[int] = None,
        include_body: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get unread messages with optional filtering.
        
        Args:
            max_results: Maximum number of messages to return
            folder: Folder/label to search in (optional)
            hours_back: Only get messages from last N hours (optional)
            include_body: Whether to include full message body
            
        Returns:
            List of standardized message dictionaries
        """
        try:
            messages = self.email_client.get_unread_messages(
                max_results=max_results,
                folder=folder,
                hours_back=hours_back
            )
            
            # Enhance messages with service-level metadata
            enhanced_messages = []
            for msg in messages:
                enhanced_msg = msg.copy()
                enhanced_msg.update({
                    'service': 'EmailService',
                    'provider': self.provider_name,
                    'retrieved_at': self._get_current_timestamp()
                })
                
                # Get full message body if requested
                if include_body and not msg.get('body'):
                    try:
                        full_msg = self.email_client.get_message(msg['id'])
                        enhanced_msg['body'] = full_msg.get('body', {})
                        enhanced_msg['attachments'] = full_msg.get('attachments', [])
                    except Exception as e:
                        self.logger.warning(f"Failed to get full body for message {msg['id']}: {e}")
                
                enhanced_messages.append(enhanced_msg)
            
            return enhanced_messages
            
        except Exception as e:
            self.logger.error(f"Failed to get unread messages: {e}")
            return [{
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }]
    
    def count_unread_messages(
        self, 
        folder: Optional[str] = None,
        hours_back: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Count unread messages with optional filtering.
        
        Args:
            folder: Folder/label to count in (optional)
            hours_back: Only count messages from last N hours (optional)
            
        Returns:
            Dict with count and filter information
        """
        try:
            count = self.email_client.count_unread_messages(
                folder=folder,
                hours_back=hours_back
            )
            
            return {
                'success': True,
                'count': count,
                'folder': folder,
                'hours_back': hours_back,
                'provider': self.provider_name,
                'service': 'EmailService',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to count unread messages: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0,
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    def search_messages(
        self, 
        query: str, 
        max_results: int = 50,
        folder: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search messages using provider-specific query syntax.
        
        Args:
            query: Search query (syntax depends on provider)
            max_results: Maximum number of results
            folder: Folder/label to search in (optional)
            
        Returns:
            List of matching message objects
        """
        try:
            # If folder is specified, modify query to include folder filter
            if folder and self.email_client.supports_feature('folders'):
                # This is provider-specific - Gmail uses labels differently than Outlook folders
                if self.provider_name == 'gmail':
                    query = f"{query} label:{folder}"
                elif self.provider_name in ['outlook', 'exchange']:
                    query = f"{query} folder:{folder}"
            
            messages = self.email_client.search_messages(query, max_results)
            
            # Add service-level metadata
            enhanced_messages = []
            for msg in messages:
                enhanced_msg = msg.copy()
                enhanced_msg.update({
                    'service': 'EmailService',
                    'provider': self.provider_name,
                    'search_query': query,
                    'retrieved_at': self._get_current_timestamp()
                })
                enhanced_messages.append(enhanced_msg)
            
            return enhanced_messages
            
        except Exception as e:
            self.logger.error(f"Failed to search messages: {e}")
            return [{
                'error': str(e),
                'query': query,
                'provider': self.provider_name,
                'service': 'EmailService'
            }]
    
    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get a complete message by ID.
        
        Args:
            message_id: The message ID
            
        Returns:
            Complete message object with body and attachments
        """
        try:
            message = self.email_client.get_message(message_id)
            
            # Add service-level metadata
            message.update({
                'service': 'EmailService',
                'provider': self.provider_name,
                'retrieved_at': self._get_current_timestamp()
            })
            
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to get message {message_id}: {e}")
            return {
                'error': str(e),
                'id': message_id,
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    # ========================================
    # MESSAGE MANAGEMENT METHODS
    # ========================================
    
    def mark_as_read(self, message_ids: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Mark message(s) as read.
        
        Args:
            message_ids: Message ID(s) to mark as read
            
        Returns:
            Dict with operation result
        """
        try:
            success = self.email_client.mark_as_read(message_ids)
            
            return {
                'success': success,
                'message_ids': message_ids if isinstance(message_ids, list) else [message_ids],
                'operation': 'mark_as_read',
                'provider': self.provider_name,
                'service': 'EmailService',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to mark messages as read: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    def mark_as_unread(self, message_ids: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Mark message(s) as unread.
        
        Args:
            message_ids: Message ID(s) to mark as unread
            
        Returns:
            Dict with operation result
        """
        try:
            success = self.email_client.mark_as_unread(message_ids)
            
            return {
                'success': success,
                'message_ids': message_ids if isinstance(message_ids, list) else [message_ids],
                'operation': 'mark_as_unread',
                'provider': self.provider_name,
                'service': 'EmailService',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to mark messages as unread: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    def delete_message(self, message_id: str, permanent: bool = False) -> Dict[str, Any]:
        """
        Delete a message.
        
        Args:
            message_id: Message ID to delete
            permanent: Whether to permanently delete (vs move to trash)
            
        Returns:
            Dict with operation result
        """
        try:
            success = self.email_client.delete_message(message_id, permanent)
            
            return {
                'success': success,
                'message_id': message_id,
                'permanent': permanent,
                'operation': 'delete_message',
                'provider': self.provider_name,
                'service': 'EmailService',
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete message {message_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    # ========================================
    # DRAFT MANAGEMENT METHODS
    # ========================================
    
    def create_draft(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        cc: Union[str, List[str]] = None,
        bcc: Union[str, List[str]] = None,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a draft message.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: HTML body (optional)
            attachments: List of file paths to attach (optional)
            
        Returns:
            Dict with draft creation result
        """
        try:
            if not self.email_client.supports_feature('drafts'):
                return {
                    'success': False,
                    'error': f"{self.provider_name} doesn't support drafts",
                    'provider': self.provider_name,
                    'service': 'EmailService'
                }
            
            result = self.email_client.create_draft(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                html_body=html_body,
                attachments=attachments
            )
            
            # Add service-level metadata
            if result.get('success', True):
                result.update({
                    'service': 'EmailService',
                    'provider': self.provider_name,
                    'timestamp': self._get_current_timestamp()
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create draft: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    def send_draft(self, draft_id: str) -> Dict[str, Any]:
        """
        Send an existing draft.
        
        Args:
            draft_id: Draft ID to send
            
        Returns:
            Dict with send result
        """
        try:
            result = self.email_client.send_draft(draft_id)
            
            # Add service-level metadata
            if result.get('success', True):
                result.update({
                    'service': 'EmailService',
                    'provider': self.provider_name,
                    'timestamp': self._get_current_timestamp()
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send draft {draft_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }
    
    # ========================================
    # FOLDER/LABEL MANAGEMENT METHODS
    # ========================================
    
    def list_folders(self) -> List[Dict[str, Any]]:
        """
        List all folders/labels.
        
        Returns:
            List of folder/label objects
        """
        try:
            folders = self.email_client.list_folders()
            
            # Add service-level metadata
            enhanced_folders = []
            for folder in folders:
                enhanced_folder = folder.copy()
                enhanced_folder.update({
                    'service': 'EmailService',
                    'provider': self.provider_name,
                    'retrieved_at': self._get_current_timestamp()
                })
                enhanced_folders.append(enhanced_folder)
            
            return enhanced_folders
            
        except Exception as e:
            self.logger.error(f"Failed to list folders: {e}")
            return [{
                'error': str(e),
                'provider': self.provider_name,
                'service': 'EmailService'
            }]
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def _validate_email_addresses(self, *address_lists) -> Dict[str, Any]:
        """
        Validate email addresses.
        
        Args:
            *address_lists: Variable number of email address lists/strings
            
        Returns:
            Dict with validation results
        """
        import re
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        all_addresses = []
        for addr_list in address_lists:
            if addr_list:
                if isinstance(addr_list, str):
                    all_addresses.append(addr_list)
                elif isinstance(addr_list, list):
                    all_addresses.extend(addr_list)
        
        invalid_addresses = []
        for addr in all_addresses:
            if not re.match(email_pattern, addr.strip()):
                invalid_addresses.append(addr)
        
        return {
            'valid': len(invalid_addresses) == 0,
            'invalid_addresses': invalid_addresses,
            'total_checked': len(all_addresses)
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    # ========================================
    # LEGACY COMPATIBILITY METHODS
    # ========================================
    
    def get_unread_count(self, **kwargs) -> int:
        """
        Legacy method for getting unread count.
        
        Args:
            **kwargs: Arguments passed to count_unread_messages
            
        Returns:
            Number of unread messages
        """
        result = self.count_unread_messages(**kwargs)
        return result.get('count', 0)
    
    def get_recent_emails(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Legacy method for getting recent emails.
        
        Args:
            **kwargs: Arguments passed to get_unread_messages
            
        Returns:
            List of recent email messages
        """
        return self.get_unread_messages(**kwargs)
