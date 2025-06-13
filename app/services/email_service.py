"""
Email Service - High-level email operations

This service abstracts Gmail operations and provides a stable API
regardless of the underlying Google API changes.
"""

from typing import List, Dict, Any, Optional
from ..modules.google_clients.gmail_client import GmailClient


class EmailService:
    """
    High-level email service that abstracts Gmail operations.
    
    Features:
    - Send emails with attachments
    - Fetch and search emails
    - Count unread messages
    - Message formatting and filtering
    """
    
    def __init__(self, config):
        self.config = config
        self._gmail_client = None
    
    @property
    def gmail_client(self) -> GmailClient:
        """Lazy initialization of Gmail client"""
        if self._gmail_client is None:
            self._gmail_client = GmailClient()
        return self._gmail_client
    
    async def send_email(
        self, 
        to: str, 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send an email with optional HTML body and attachments.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            attachments: Optional list of file paths to attach
            
        Returns:
            Dict with success status and message ID or error info
        """
        try:
            message_id = self.gmail_client.send_message(
                to=to,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments or []
            )
            return {
                "success": True,
                "message_id": message_id,
                "message": "Email sent successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send email"
            }
    
    def get_unread_messages(
        self, 
        max_results: int = 10,
        category: Optional[str] = None,
        hours_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get unread messages with optional filtering.
        
        Args:
            max_results: Maximum number of messages to return
            category: Optional Gmail category filter
            hours_back: Optional time filter in hours
            
        Returns:
            List of formatted message dictionaries
        """
        try:
            return self.gmail_client.list_unread_messages(
                max_results=max_results,
                category=category,
                hours_back=hours_back
            )
        except Exception as e:
            return [{
                "error": str(e),
                "message": "Failed to fetch unread messages"
            }]
    
    def count_unread_messages(
        self, 
        category: Optional[str] = None,
        hours_back: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Count unread messages with optional filtering.
        
        Returns:
            Dict with count and filter info
        """
        try:
            count = self.gmail_client.count_unread_messages(
                category=category,
                hours_back=hours_back
            )
            return {
                "success": True,
                "count": count,
                "category": category,
                "hours_back": hours_back
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "count": 0
            }
    
    def search_messages(
        self, 
        query: str, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search messages using Gmail search syntax.
        
        Args:
            query: Gmail search query (e.g., "from:example@gmail.com")
            max_results: Maximum number of results
            
        Returns:
            List of matching messages
        """
        try:
            return self.gmail_client.search_messages(query, max_results)
        except Exception as e:
            return [{
                "error": str(e),
                "message": f"Failed to search messages with query: {query}"
            }]
