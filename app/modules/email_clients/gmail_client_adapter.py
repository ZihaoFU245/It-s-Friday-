"""
Gmail Client Adapter

This module provides a Gmail-specific implementation of the BaseEmailClient interface.
It adapts the existing GmailClient to work with the standardized email service interface.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone, timedelta
import logging

from .base_email_client import BaseEmailClient
from ..google_clients.gmail_client import GmailClient as GoogleGmailClient


class GmailClientAdapter(BaseEmailClient):
    """
    Gmail implementation of the BaseEmailClient interface.
    
    This adapter wraps the existing GmailClient and provides a standardized
    interface that can be used interchangeably with other email providers.
    
    Features:
    - Full Gmail API integration
    - Message threading support
    - Advanced search capabilities
    - Label management
    - Draft operations
    - Attachment handling    
    """
    
    def __init__(self, config=None, **kwargs):
        """
        Initialize the Gmail client adapter.
        
        Args:
            config: EmailConfig object containing account-specific configuration (required)
            **kwargs: Additional keyword arguments for future extensibility
        """
        super().__init__()
        self.config = config  # Store for future use if needed
        
        # Extract Google-specific paths from config
        if not config:
            raise ValueError("EmailConfig is required for Gmail client initialization")
        
        if not hasattr(config, 'google_credentials_path') or not config.google_credentials_path:
            raise ValueError("Google credentials path is required for Gmail client")
        
        if not hasattr(config, 'google_token_path') or not config.google_token_path:
            raise ValueError("Google token path is required for Gmail client")
        
        credentials_path = str(config.google_credentials_path)
        token_path = str(config.google_token_path)
        
        # Initialize Gmail client with required account-specific paths
        self._gmail_client = GoogleGmailClient(
            credentials_path=credentials_path,
            token_path=token_path
        )
        self.logger = logging.getLogger(__name__)
    
    # ========================================
    # AUTHENTICATION AND PROFILE METHODS
    # ========================================
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Get the user's Gmail profile information.
        
        Returns:
            Dict containing standardized profile information
        """
        try:
            gmail_profile = self._gmail_client.get_profile()
            return {
                'email_address': gmail_profile.get('emailAddress'),
                'display_name': gmail_profile.get('emailAddress', '').split('@')[0],
                'total_messages': gmail_profile.get('messagesTotal', 0),
                'total_threads': gmail_profile.get('threadsTotal', 0),
                'provider': 'gmail',
                'account_type': 'google',
                'history_id': gmail_profile.get('historyId'),
                'raw_profile': gmail_profile
            }
        except Exception as e:
            self.logger.error(f"Failed to get Gmail profile: {e}")
            raise
    
    # ========================================
    # MESSAGE SENDING METHODS
    # ========================================
    
    def send_email(
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
        Send an email message via Gmail.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: HTML body (optional)
            attachments: List of file paths to attach (optional)
            
        Returns:
            Standardized response dict
        """
        try:
            result = self._gmail_client.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                html_body=html_body,
                attachments=attachments or []
            )
            
            return {
                'id': result.get('id'),
                'thread_id': result.get('threadId'),
                'success': True,
                'provider': 'gmail',
                'provider_response': result
            }
        except Exception as e:
            self.logger.error(f"Failed to send email via Gmail: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gmail'
            }
    
    def reply_to_message(
        self, 
        message_id: str, 
        body: str,
        html_body: Optional[str] = None,
        reply_all: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Reply to an existing Gmail message.
        
        Args:
            message_id: ID of the message to reply to
            body: Reply body text
            html_body: Reply HTML body (optional)
            reply_all: Whether to reply to all recipients
            attachments: List of file paths to attach (optional)
            
        Returns:
            Standardized response dict
        """
        try:
            result = self._gmail_client.reply_to_message(
                msg_id=message_id,
                body=body,
                html_body=html_body,
                reply_all=reply_all,
                attachments=attachments or []
            )
            
            return {
                'id': result.get('id'),
                'thread_id': result.get('threadId'),
                'success': True,
                'provider': 'gmail',
                'provider_response': result
            }
        except Exception as e:
            self.logger.error(f"Failed to reply to Gmail message {message_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gmail'
            }
    
    # ========================================
    # MESSAGE RETRIEVAL METHODS
    # ========================================
    
    def list_messages(
        self, 
        max_results: int = 10, 
        query: str = "", 
        folder: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List Gmail messages with optional filtering.
        
        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query
            folder: Label ID to filter by (optional)
            
        Returns:
            List of standardized message metadata
        """
        try:
            # Convert folder name to label ID if needed
            label_ids = None
            if folder:
                label_ids = [folder] if not folder.startswith('LABEL_') else [folder]
            
            messages = self._gmail_client.list_messages(
                max_results=max_results,
                query=query,
                label_ids=label_ids
            )
            
            # Convert to standardized format
            standardized_messages = []
            for msg in messages:
                try:
                    # Get basic message info without full retrieval for performance
                    standardized_messages.append({
                        'id': msg.get('id'),
                        'thread_id': msg.get('threadId'),
                        'provider': 'gmail',
                        'raw_message': msg
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to process message {msg.get('id', 'unknown')}: {e}")
                    continue
            
            return standardized_messages
        except Exception as e:
            self.logger.error(f"Failed to list Gmail messages: {e}")
            return []
    
    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get a complete Gmail message by ID.
        
        Args:
            message_id: The message ID
            
        Returns:
            Standardized message dict
        """
        try:
            raw_message = self._gmail_client.get_raw_message(message_id)
            formatted_message = self._gmail_client.get_formatted_message(raw_message)
            
            return {
                'id': formatted_message.get('id'),
                'thread_id': formatted_message.get('threadId'),
                'subject': formatted_message.get('subject'),
                'from': formatted_message.get('from'),
                'to': formatted_message.get('to'),
                'cc': formatted_message.get('cc'),
                'bcc': formatted_message.get('bcc'),
                'date': formatted_message.get('date'),
                'internal_date': formatted_message.get('internalDate'),
                'body': formatted_message.get('body', {}),
                'attachments': formatted_message.get('attachments', []),
                'labels': formatted_message.get('labelIds', []),
                'is_read': 'UNREAD' not in formatted_message.get('labelIds', []),
                'snippet': formatted_message.get('snippet'),
                'provider': 'gmail',
                'raw_message': raw_message,
                'formatted_message': formatted_message
            }
        except Exception as e:
            self.logger.error(f"Failed to get Gmail message {message_id}: {e}")
            raise
    
    def search_messages(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search Gmail messages using Gmail query syntax.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results
            
        Returns:
            List of standardized message objects
        """
        try:
            messages = self._gmail_client.search_messages(query, max_results)
            
            # Convert to standardized format
            standardized_messages = []
            for msg in messages:
                try:
                    standardized_msg = {
                        'id': msg.get('id'),
                        'thread_id': msg.get('threadId'),
                        'subject': msg.get('subject'),
                        'from': msg.get('from'),
                        'to': msg.get('to'),
                        'date': msg.get('date'),
                        'snippet': msg.get('snippet'),
                        'is_read': msg.get('is_read', True),
                        'provider': 'gmail',
                        'formatted_message': msg
                    }
                    standardized_messages.append(standardized_msg)
                except Exception as e:
                    self.logger.warning(f"Failed to process search result: {e}")
                    continue
            
            return standardized_messages
        except Exception as e:
            self.logger.error(f"Failed to search Gmail messages: {e}")
            return []
    
    # ========================================
    # MESSAGE MANAGEMENT METHODS
    # ========================================
    
    def mark_as_read(self, message_ids: Union[str, List[str]]) -> bool:
        """
        Mark Gmail message(s) as read.
        
        Args:
            message_ids: Message ID(s) to mark as read
            
        Returns:
            Boolean indicating success
        """
        try:
            self._gmail_client.mark_as_read(message_ids)
            return True
        except Exception as e:
            self.logger.error(f"Failed to mark Gmail messages as read: {e}")
            return False
    
    def mark_as_unread(self, message_ids: Union[str, List[str]]) -> bool:
        """
        Mark Gmail message(s) as unread.
        
        Args:
            message_ids: Message ID(s) to mark as unread
            
        Returns:
            Boolean indicating success
        """
        try:
            self._gmail_client.mark_as_unread(message_ids)
            return True
        except Exception as e:
            self.logger.error(f"Failed to mark Gmail messages as unread: {e}")
            return False
    
    def delete_message(self, message_id: str, permanent: bool = False) -> bool:
        """
        Delete a Gmail message.
        
        Args:
            message_id: Message ID to delete
            permanent: Whether to permanently delete (vs move to trash)
            
        Returns:
            Boolean indicating success
        """
        try:
            if permanent:
                self._gmail_client.delete_message(message_id)
            else:
                self._gmail_client.trash_message(message_id)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete Gmail message {message_id}: {e}")
            return False
    
    def move_to_folder(self, message_id: str, folder: str) -> bool:
        """
        Move a Gmail message to a specific label.
        
        Args:
            message_id: Message ID to move
            folder: Target label name or ID
            
        Returns:
            Boolean indicating success
        """
        try:
            # Remove from current labels and add to new one
            # For Gmail, this means managing labels
            self._gmail_client.add_labels(message_id, [folder])
            return True
        except Exception as e:
            self.logger.error(f"Failed to move Gmail message {message_id} to {folder}: {e}")
            return False
    
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
        Create a Gmail draft message.
        
        Returns:
            Standardized draft response dict
        """
        try:
            result = self._gmail_client.create_draft(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                html_body=html_body,
                attachments=attachments or []
            )
            
            return {
                'id': result.get('id'),
                'message_id': result.get('message', {}).get('id'),
                'success': True,
                'provider': 'gmail',
                'provider_response': result
            }
        except Exception as e:
            self.logger.error(f"Failed to create Gmail draft: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gmail'
            }
    
    def update_draft(self, draft_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing Gmail draft.
        
        Args:
            draft_id: Draft ID to update
            **kwargs: Fields to update (to, subject, body, etc.)
            
        Returns:
            Standardized draft response dict
        """
        try:
            result = self._gmail_client.update_draft(draft_id, **kwargs)
            
            return {
                'id': result.get('id'),
                'message_id': result.get('message', {}).get('id'),
                'success': True,
                'provider': 'gmail',
                'provider_response': result
            }
        except Exception as e:
            self.logger.error(f"Failed to update Gmail draft {draft_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gmail'
            }
    
    def send_draft(self, draft_id: str) -> Dict[str, Any]:
        """
        Send an existing Gmail draft.
        
        Args:
            draft_id: Draft ID to send
            
        Returns:
            Standardized response dict
        """
        try:
            result = self._gmail_client.send_draft(draft_id)
            
            return {
                'id': result.get('id'),
                'thread_id': result.get('threadId'),
                'success': True,
                'provider': 'gmail',
                'provider_response': result
            }
        except Exception as e:
            self.logger.error(f"Failed to send Gmail draft {draft_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gmail'
            }
    
    def delete_draft(self, draft_id: str) -> bool:
        """
        Delete a Gmail draft.
        
        Args:
            draft_id: Draft ID to delete
            
        Returns:
            Boolean indicating success
        """
        try:
            self._gmail_client.delete_draft(draft_id)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete Gmail draft {draft_id}: {e}")
            return False
    
    def list_drafts(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List Gmail draft messages.
        
        Args:
            max_results: Maximum number of drafts to return
            
        Returns:
            List of standardized draft objects
        """
        try:
            drafts = self._gmail_client.list_drafts(max_results)
            
            standardized_drafts = []
            for draft in drafts:
                standardized_drafts.append({
                    'id': draft.get('id'),
                    'message_id': draft.get('message', {}).get('id'),
                    'provider': 'gmail',
                    'raw_draft': draft
                })
            
            return standardized_drafts
        except Exception as e:
            self.logger.error(f"Failed to list Gmail drafts: {e}")
            return []
    
    # ========================================
    # FOLDER/LABEL MANAGEMENT METHODS
    # ========================================
    
    def list_folders(self) -> List[Dict[str, Any]]:
        """
        List all Gmail labels (folders).
        
        Returns:
            List of standardized folder objects
        """
        try:
            labels = self._gmail_client.list_labels()
            
            standardized_folders = []
            for label in labels:
                standardized_folders.append({
                    'id': label.get('id'),
                    'name': label.get('name'),
                    'type': label.get('type', 'user'),
                    'message_count': label.get('messagesTotal', 0),
                    'unread_count': label.get('messagesUnread', 0),
                    'provider': 'gmail',
                    'raw_label': label
                })
            
            return standardized_folders
        except Exception as e:
            self.logger.error(f"Failed to list Gmail labels: {e}")
            return []
    
    def create_folder(self, name: str, parent_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Gmail label.
        
        Args:
            name: Label name
            parent_folder: Parent folder ID (Gmail doesn't support nested labels directly)
            
        Returns:
            Standardized folder response dict
        """
        try:
            # Gmail doesn't support nested labels, but we can use naming convention
            if parent_folder:
                # Use nested naming convention
                full_name = f"{parent_folder}/{name}"
            else:
                full_name = name
                
            result = self._gmail_client.create_label(full_name)
            
            return {
                'id': result.get('id'),
                'name': result.get('name'),
                'success': True,
                'provider': 'gmail',
                'provider_response': result
            }
        except Exception as e:
            self.logger.error(f"Failed to create Gmail label {name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gmail'
            }
    
    def delete_folder(self, folder_id: str) -> bool:
        """
        Delete a Gmail label.
        
        Args:
            folder_id: Label ID to delete
            
        Returns:
            Boolean indicating success
        """
        try:
            self._gmail_client.delete_label(folder_id)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete Gmail label {folder_id}: {e}")
            return False
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def count_unread_messages(
        self, 
        folder: Optional[str] = None, 
        hours_back: Optional[int] = None
    ) -> int:
        """
        Count unread Gmail messages.
        
        Args:
            folder: Label to count in (optional)
            hours_back: Only count messages from last N hours (optional)
            
        Returns:
            Number of unread messages
        """
        try:
            return self._gmail_client.count_unread(
                hours=hours_back or 24,
                category=folder or "PRIMARY"
            )
        except Exception as e:
            self.logger.error(f"Failed to count unread Gmail messages: {e}")
            return 0
    
    def get_unread_messages(
        self, 
        max_results: int = 10,
        folder: Optional[str] = None,
        hours_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get unread Gmail messages.
        
        Args:
            max_results: Maximum number of messages to return
            folder: Label to search in (optional)
            hours_back: Only get messages from last N hours (optional)
            
        Returns:
            List of standardized unread message objects
        """
        try:
            messages = self._gmail_client.fetch_unread(
                hours=hours_back or 24,
                max_results=max_results,
                category=folder or "PRIMARY"
            )
            
            # Convert to standardized format
            standardized_messages = []
            for msg in messages:
                standardized_msg = {
                    'id': msg.get('id'),
                    'thread_id': msg.get('threadId'),
                    'subject': msg.get('subject'),
                    'from': msg.get('from'),
                    'to': msg.get('to'),
                    'date': msg.get('date'),
                    'snippet': msg.get('snippet'),
                    'is_read': False,  # These are unread messages
                    'provider': 'gmail',
                    'formatted_message': msg
                }
                standardized_messages.append(standardized_msg)
            
            return standardized_messages
        except Exception as e:
            self.logger.error(f"Failed to get unread Gmail messages: {e}")
            return []
    
    # ========================================
    # PROVIDER-SPECIFIC METHODS
    # ========================================
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return 'gmail'
    
    def supports_feature(self, feature: str) -> bool:
        """
        Check if Gmail supports a specific feature.
        
        Args:
            feature: Feature name to check
            
        Returns:
            Boolean indicating if feature is supported
        """
        gmail_features = {
            'html_email': True,
            'attachments': True,
            'threading': True,
            'labels': True,
            'folders': True,  # Via labels
            'search': True,
            'drafts': True,
            'advanced_search': True,
            'batch_operations': True,
            'push_notifications': True,
            'history_api': True
        }
        
        return gmail_features.get(feature, False)
    
    def get_raw_api_client(self):
        """
        Get access to the underlying Gmail API client.
        
        Returns:
            The Gmail client service object
        """
        return self._gmail_client.service
    
    def get_gmail_client(self) -> GoogleGmailClient:
        """
        Get the underlying Gmail client for Gmail-specific operations.
        
        Returns:
            The GmailClient instance
        """
        return self._gmail_client
