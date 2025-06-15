"""
Abstract Base Email Client

This module defines the interface that all email clients must implement.
This abstraction allows the EmailService to work with different email providers
(Gmail, Outlook, etc.) without code changes.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime


class BaseEmailClient(ABC):
    """
    Abstract base class defining the interface for all email clients.
    
    This interface ensures that all email client implementations provide
    the same methods with consistent signatures, allowing the EmailService
    to work with any email provider seamlessly.
    
    Implementing classes must provide:
    - Authentication and connection management
    - Message sending (with attachments and HTML support)
    - Message retrieval and search
    - Draft management
    - Label/folder management
    - Message operations (read/unread, delete, etc.)
    """
    
    def __init__(self):
        """Initialize the email client. Subclasses should handle authentication."""
        pass
    
    # ========================================
    # AUTHENTICATION AND PROFILE METHODS
    # ========================================
    
    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        """
        Get the user's email profile information.
        
        Returns:
            Dict containing:
                - email_address: User's email address
                - display_name: User's display name (if available)
                - total_messages: Total number of messages
                - provider: Email provider name (e.g., 'gmail', 'outlook')
                - account_type: Account type (e.g., 'personal', 'business')
        """
        pass
    
    # ========================================
    # MESSAGE SENDING METHODS
    # ========================================
    
    @abstractmethod
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
        Send an email message.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Plain text body
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: HTML body (optional)
            attachments: List of file paths to attach (optional)
            
        Returns:
            Dict containing:
                - id: Message ID
                - thread_id: Thread ID (if supported)
                - success: Boolean indicating success
                - provider_response: Original provider response
        """
        pass
    
    @abstractmethod
    def reply_to_message(
        self, 
        message_id: str, 
        body: str,
        html_body: Optional[str] = None,
        reply_all: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Reply to an existing message.
        
        Args:
            message_id: ID of the message to reply to
            body: Reply body text
            html_body: Reply HTML body (optional)
            reply_all: Whether to reply to all recipients
            attachments: List of file paths to attach (optional)
            
        Returns:
            Dict containing sent reply information
        """
        pass
    
    # ========================================
    # MESSAGE RETRIEVAL METHODS
    # ========================================
    
    @abstractmethod
    def list_messages(
        self, 
        max_results: int = 10, 
        query: str = "", 
        folder: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List messages with optional filtering.
        
        Args:
            max_results: Maximum number of messages to return
            query: Search query (provider-specific syntax)
            folder: Folder/label to search in (optional)
            
        Returns:
            List of message metadata dictionaries
        """
        pass
    
    @abstractmethod
    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get a complete message by ID.
        
        Args:
            message_id: The message ID
            
        Returns:
            Dict containing:
                - id: Message ID
                - thread_id: Thread ID
                - subject: Message subject
                - from: Sender information
                - to: Recipient information
                - cc: CC recipients
                - bcc: BCC recipients
                - date: Message date
                - body: Dict with 'text' and 'html' content
                - attachments: List of attachment info
                - labels: List of labels/folders
                - is_read: Read status
        """
        pass
    
    @abstractmethod
    def search_messages(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for messages using provider-specific query syntax.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of matching message objects
        """
        pass
    
    # ========================================
    # MESSAGE MANAGEMENT METHODS
    # ========================================
    
    @abstractmethod
    def mark_as_read(self, message_ids: Union[str, List[str]]) -> bool:
        """
        Mark message(s) as read.
        
        Args:
            message_ids: Message ID(s) to mark as read
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def mark_as_unread(self, message_ids: Union[str, List[str]]) -> bool:
        """
        Mark message(s) as unread.
        
        Args:
            message_ids: Message ID(s) to mark as unread
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def delete_message(self, message_id: str, permanent: bool = False) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: Message ID to delete
            permanent: Whether to permanently delete (vs move to trash)
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def move_to_folder(self, message_id: str, folder: str) -> bool:
        """
        Move a message to a specific folder.
        
        Args:
            message_id: Message ID to move
            folder: Target folder name
            
        Returns:
            Boolean indicating success
        """
        pass
    
    # ========================================
    # DRAFT MANAGEMENT METHODS
    # ========================================
    
    @abstractmethod
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
            Dict containing draft information
        """
        pass
    
    @abstractmethod
    def update_draft(self, draft_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing draft.
        
        Args:
            draft_id: Draft ID to update
            **kwargs: Fields to update (to, subject, body, etc.)
            
        Returns:
            Dict containing updated draft information
        """
        pass
    
    @abstractmethod
    def send_draft(self, draft_id: str) -> Dict[str, Any]:
        """
        Send an existing draft.
        
        Args:
            draft_id: Draft ID to send
            
        Returns:
            Dict containing sent message information
        """
        pass
    
    @abstractmethod
    def delete_draft(self, draft_id: str) -> bool:
        """
        Delete a draft.
        
        Args:
            draft_id: Draft ID to delete
            
        Returns:
            Boolean indicating success
        """
        pass
    
    @abstractmethod
    def list_drafts(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List draft messages.
        
        Args:
            max_results: Maximum number of drafts to return
            
        Returns:
            List of draft objects
        """
        pass
    
    # ========================================
    # FOLDER/LABEL MANAGEMENT METHODS
    # ========================================
    
    @abstractmethod
    def list_folders(self) -> List[Dict[str, Any]]:
        """
        List all folders/labels.
        
        Returns:
            List of folder/label objects containing:
                - id: Folder ID
                - name: Folder name
                - type: Folder type (system/user)
                - message_count: Number of messages (if available)
        """
        pass
    
    @abstractmethod
    def create_folder(self, name: str, parent_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new folder/label.
        
        Args:
            name: Folder name
            parent_folder: Parent folder ID (for nested folders)
            
        Returns:
            Dict containing created folder information
        """
        pass
    
    @abstractmethod
    def delete_folder(self, folder_id: str) -> bool:
        """
        Delete a folder/label.
        
        Args:
            folder_id: Folder ID to delete
            
        Returns:
            Boolean indicating success
        """
        pass
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    @abstractmethod
    def count_unread_messages(
        self, 
        folder: Optional[str] = None, 
        hours_back: Optional[int] = None
    ) -> int:
        """
        Count unread messages with optional filtering.
        
        Args:
            folder: Folder to count in (optional)
            hours_back: Only count messages from last N hours (optional)
            
        Returns:
            Number of unread messages
        """
        pass
    
    @abstractmethod
    def get_unread_messages(
        self, 
        max_results: int = 10,
        folder: Optional[str] = None,
        hours_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get unread messages with optional filtering.
        
        Args:
            max_results: Maximum number of messages to return
            folder: Folder to search in (optional)
            hours_back: Only get messages from last N hours (optional)
            
        Returns:
            List of unread message objects
        """
        pass
    
    # ========================================
    # PROVIDER-SPECIFIC METHODS
    # ========================================
    
    def get_provider_name(self) -> str:
        """
        Get the name of the email provider.
        
        Returns:
            String identifying the provider (e.g., 'gmail', 'outlook')
        """
        return self.__class__.__name__.lower().replace('client', '')
    
    def supports_feature(self, feature: str) -> bool:
        """
        Check if the provider supports a specific feature.
        
        Args:
            feature: Feature name to check
            
        Returns:
            Boolean indicating if feature is supported
            
        Common features:
            - 'html_email': HTML email support
            - 'attachments': File attachment support
            - 'threading': Email threading support
            - 'labels': Label/tag support
            - 'folders': Folder hierarchy support
            - 'search': Advanced search support
            - 'drafts': Draft message support
        """
        # Default implementation - subclasses should override
        return True
    
    def get_raw_api_client(self):
        """
        Get access to the underlying API client for provider-specific operations.
        
        Returns:
            The raw API client object (use with caution)
        """
        # Default implementation returns None - subclasses may override
        return None
