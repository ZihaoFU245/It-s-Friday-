"""
Email Manager - Multi-account email service management

This module provides management for multiple email accounts, allowing the application
to work with personal, work, and other email accounts simultaneously.

Features:
- Multi-account support (personal, work, etc.)
- Account-specific operations
- Unified interface for all accounts
- Account discovery and validation
- Provider-agnostic operations across accounts
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..config import Config
from ..modules.email_clients import BaseEmailClient
from ..utils import EmailAccountManager


class EmailManager:
    """
    Manager for multiple email accounts and services.
    
    This class handles the creation and management of multiple EmailService instances,
    one for each configured email account. It provides a unified interface for
    operations across multiple accounts.
    
    Features:
    - Automatic account discovery from configuration
    - Lazy initialization of email services
    - Account-specific operations
    - Unified operations across all accounts
    - Account validation and error handling
    - Provider-agnostic multi-account support
    
    Usage:
        # Initialize with configuration
        email_manager = EmailManager(config)
        
        # Send from specific account
        result = await email_manager.send_email(
            account="work",
            to="colleague@company.com",
            subject="Meeting",
            body="Let's meet tomorrow"
        )
          # Get unread from all accounts
        all_unread = email_manager.get_all_unread_messages()
        
        # Get unread from specific account
        work_unread = email_manager.get_unread_messages(account="work")
    """
    
    def __init__(self, config: Config):
        """
        Initialize the email manager.
        
        Args:
            config: Configuration object containing email account settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)        
        # Use EmailAccountManager for client management
        self.account_manager = EmailAccountManager(config)
        
        # Cache for account information
        self._account_info_cache: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info(f"EmailManager initialized with {len(config.email_accounts)} configured accounts")
    
    @property
    def available_accounts(self) -> List[str]:
        """Get list of available account names."""
        return [acc.name for acc in self.config.list_email_accounts(enabled_only=True)]
    
    def get_email_client(self, account_name: str) -> BaseEmailClient:
        """
        Get email client for a specific account using the AccountManager.
        
        Args:
            account_name: Name of the email account
            
        Returns:
            BaseEmailClient instance for the account
            
        Raises:
            ValueError: If account is not configured, disabled, or client creation fails
        """
        try:
            # Try to get existing client first
            return self.account_manager.get_email_client(account_name)
        except ValueError:
            # If client doesn't exist, create it
            return self.account_manager.create_email_client(account_name)
    
    def get_default_account(self) -> str:
        """
        Get the name of the default email account.
        
        Returns:
            Name of the default account
            
        Raises:
            ValueError: If no default account is configured
        """
        default_account = self.config.get_default_email_account()
        if not default_account:
            raise ValueError("No default email account configured")
        return default_account.name
    
    # ========================================
    # EMAIL SENDING METHODS
    # ========================================
    
    async def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        account: Optional[str] = None,
        cc: Union[str, List[str]] = None,
        bcc: Union[str, List[str]] = None,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send email from a specific account.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body
            account: Account name to send from (uses default if not specified)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: HTML body (optional)
            attachments: File attachments (optional)
            **kwargs: Additional arguments for the email service
              Returns:
            Dict with send result and account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            # Check if account exists in our configuration
            account_config = self.account_manager.get_account_config(account)
            if not account_config:
                return {
                    'success': False,
                    'error': 'accounts must be added before use',
                    'account': account,
                    'manager': 'EmailManager'
                }
            
            email_client = self.get_email_client(account)
            
            result = email_client.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                html_body=html_body,
                attachments=attachments
            )
            
            # Add account information to result
            if isinstance(result, dict):
                result['account'] = account
                result['manager'] = 'EmailManager'
            else:
                # If result is not a dict, create a standardized response
                result = {
                    'success': True,
                    'account': account,
                    'manager': 'EmailManager',
                    'result': result
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send email from account '{account}': {e}")
            return {
                'success': False,
                'error': str(e),
                'account': account,
                'manager': 'EmailManager'
            }
    
    # ========================================
    # EMAIL RETRIEVAL METHODS
    # ========================================
    
    def get_unread_messages(
        self,
        account: Optional[str] = None,
        max_results: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get unread messages from a specific account.
        
        Args:
            account: Account name (uses default if not specified)
            max_results: Maximum number of messages to return
            **kwargs: Additional arguments for the email service
              Returns:
            List of unread messages with account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            # Check if account exists in our configuration
            account_config = self.account_manager.get_account_config(account)
            if not account_config:
                self.logger.error(f"Account '{account}' not found in configuration")
                return []
            
            email_client = self.get_email_client(account)
            messages = email_client.get_unread_messages(max_results=max_results)
            
            # Add account information to each message
            if isinstance(messages, list):
                for message in messages:
                    if isinstance(message, dict):
                        message['account'] = account
            
            return messages if isinstance(messages, list) else []
            
        except Exception as e:
            self.logger.error(f"Failed to get unread messages from account '{account}': {e}")
            return []
    
    def get_all_unread_messages(self, max_results_per_account: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get unread messages from all enabled accounts.
        
        Args:
            max_results_per_account: Maximum messages per account
            
        Returns:
            Dict mapping account names to lists of unread messages
        """
        all_messages = {}
        
        for account_name in self.available_accounts:
            try:
                messages = self.get_unread_messages(
                    account=account_name,
                    max_results=max_results_per_account
                )
                all_messages[account_name] = messages
                
            except Exception as e:
                self.logger.error(f"Failed to get messages from account '{account_name}': {e}")
                all_messages[account_name] = []
        
        return all_messages
    
    def count_unread_messages(self, account: Optional[str] = None) -> Dict[str, Any]:
        """
        Count unread messages in a specific account.
        
        Args:
            account: Account name (uses default if not specified)
              Returns:
            Dict with unread count and account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            count = email_client.count_unread_messages()
            
            # Return standardized format
            return {
                'success': True,
                'count': count if isinstance(count, int) else 0,
                'account': account
            }
            
        except Exception as e:
            self.logger.error(f"Failed to count unread messages from account '{account}': {e}")
            return {
                'success': False,
                'error': str(e),
                'account': account,
                'count': 0
            }
    
    def count_all_unread_messages(self) -> Dict[str, Dict[str, Any]]:
        """
        Count unread messages across all enabled accounts.
        
        Returns:
            Dict mapping account names to unread count information
        """
        all_counts = {}
        
        for account_name in self.available_accounts:
            all_counts[account_name] = self.count_unread_messages(account=account_name)
        
        return all_counts
    
    # ========================================
    # ACCOUNT MANAGEMENT METHODS
    # ========================================
    
    def get_account_info(self, account: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a specific account.
        
        Args:
            account: Account name (uses default if not specified)
              Returns:
            Dict with account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            if account in self._account_info_cache:
                return self._account_info_cache[account]
            
            email_client = self.get_email_client(account)
            
            # Get profile information from the client
            if hasattr(email_client, 'get_profile'):
                info = email_client.get_profile()
            else:
                info = {'email_address': 'unknown', 'display_name': 'Unknown'}
            
            info['account_name'] = account
            
            # Cache the information
            self._account_info_cache[account] = info
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get info for account '{account}': {e}")
            return {
                'success': False,
                'error': str(e),
                'account': account
            }
    
    def get_all_account_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all enabled accounts.
        
        Returns:
            Dict mapping account names to account information
        """
        all_info = {}
        
        for account_name in self.available_accounts:
            all_info[account_name] = self.get_account_info(account=account_name)
        
        return all_info
    
    def validate_account(self, account: str) -> Dict[str, Any]:
        """
        Validate that an account is properly configured and accessible.
        
        Args:
            account: Account name to validate
              Returns:
            Dict with validation result
        """
        try:
            email_client = self.get_email_client(account)
            
            # Try to get profile to validate connection
            if hasattr(email_client, 'get_profile'):
                info = email_client.get_profile()
                email_address = info.get('email_address', 'unknown')
            else:
                email_address = 'unknown'
            
            account_config = self.config.get_email_account_config(account)
            
            return {
                'success': True,
                'account': account,
                'provider': account_config.provider if account_config else 'unknown',
                'email_address': email_address,
                'valid': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'account': account,
                'error': str(e),
                'valid': False
            }
    
    def validate_all_accounts(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all configured accounts.
        
        Returns:
            Dict mapping account names to validation results
        """
        results = {}
        
        for account_name in self.available_accounts:
            results[account_name] = self.validate_account(account_name)
        
        return results
    
    # ========================================
    # MESSAGE MANAGEMENT METHODS
    # ========================================
    
    def mark_as_read(
        self,
        message_ids: Union[str, List[str]],
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark message(s) as read in a specific account.
        
        Args:
            message_ids: Message ID(s) to mark as read
            account: Account name (uses default if not specified)
              Returns:
            Dict with operation result and account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            success = email_client.mark_as_read(message_ids)
            
            return {
                'success': success,
                'message_ids': message_ids if isinstance(message_ids, list) else [message_ids],
                'operation': 'mark_as_read',
                'account': account,
                'manager': 'EmailManager'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to mark messages as read from account '{account}': {e}")
            return {
                'success': False,
                'error': str(e),
                'account': account,
                'manager': 'EmailManager'
            }
    
    def mark_as_unread(
        self,
        message_ids: Union[str, List[str]],
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark message(s) as unread in a specific account.
        
        Args:
            message_ids: Message ID(s) to mark as unread
            account: Account name (uses default if not specified)
              Returns:
            Dict with operation result and account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            success = email_client.mark_as_unread(message_ids)
            
            return {
                'success': success,
                'message_ids': message_ids if isinstance(message_ids, list) else [message_ids],
                'operation': 'mark_as_unread',
                'account': account,
                'manager': 'EmailManager'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to mark messages as unread from account '{account}': {e}")
            return {
                'success': False,
                'error': str(e),
                'account': account,
                'manager': 'EmailManager'
            }
    
    def delete_message(
        self,
        message_id: str,
        account: Optional[str] = None,
        permanent: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a message from a specific account.
        
        Args:
            message_id: Message ID to delete
            account: Account name (uses default if not specified)
            permanent: Whether to permanently delete (vs move to trash)
              Returns:
            Dict with operation result and account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            success = email_client.delete_message(message_id, permanent)
            
            return {
                'success': success,
                'message_id': message_id,
                'permanent': permanent,
                'operation': 'delete_message',
                'account': account,
                'manager': 'EmailManager'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete message from account '{account}': {e}")
            return {
                'success': False,
                'error': str(e),
                'account': account,
                'manager': 'EmailManager'
            }
    
    # ========================================
    # DRAFT MANAGEMENT METHODS
    # ========================================
    
    async def create_draft(
        self,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        account: Optional[str] = None,
        cc: Union[str, List[str]] = None,
        bcc: Union[str, List[str]] = None,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a draft message in a specific account.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body
            account: Account name (uses default if not specified)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: HTML body (optional)
            attachments: File attachments (optional)
              Returns:
            Dict with draft creation result and account information
        """
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            
            # Check if the client supports drafts
            if not hasattr(email_client, 'create_draft'):
                return {
                    'success': False,
                    'error': f"Draft creation not supported by this email provider",
                    'account': account,
                    'manager': 'EmailManager'
                }
            
            result = email_client.create_draft(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                html_body=html_body,
                attachments=attachments
            )
            
            # Ensure result is a dict and add account info
            if isinstance(result, dict):
                result['account'] = account
                result['manager'] = 'EmailManager'
            else:
                result = {
                    'success': True,
                    'draft_id': result,
                    'account': account,
                    'manager': 'EmailManager'
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create draft in account '{account}': {e}")
            return {
                'success': False,
                'error': str(e),
                'account': account,
                'manager': 'EmailManager'
            }
    
    async def update_draft(
        self,
        draft_id: str,
        to: Union[str, List[str]],
        subject: str,
        body: str,
        account: Optional[str] = None,
        cc: Union[str, List[str]] = None,
        bcc: Union[str, List[str]] = None,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update an existing draft in a specific account."""
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            
            if hasattr(email_client, 'update_draft'):
                result = email_client.update_draft(
                    draft_id=draft_id, to=to, subject=subject, body=body,
                    cc=cc, bcc=bcc, html_body=html_body, attachments=attachments
                )
            else:
                result = {'success': False, 'error': 'Update draft not supported'}
            
            if isinstance(result, dict):
                result['account'] = account
                result['manager'] = 'EmailManager'
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e), 'account': account, 'manager': 'EmailManager'}

    async def send_draft(self, draft_id: str, account: Optional[str] = None) -> Dict[str, Any]:
        """Send an existing draft from a specific account."""
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            result = email_client.send_draft(draft_id)
            
            if isinstance(result, dict):
                result['account'] = account
                result['manager'] = 'EmailManager'
            else:
                result = {'success': True, 'account': account, 'manager': 'EmailManager'}
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e), 'account': account, 'manager': 'EmailManager'}

    def list_drafts(self, account: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """List drafts from a specific account."""
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            
            if hasattr(email_client, 'list_drafts'):
                drafts = email_client.list_drafts(max_results)
                if isinstance(drafts, list):
                    for draft in drafts:
                        if isinstance(draft, dict):
                            draft['account'] = account
                            draft['manager'] = 'EmailManager'
                    return drafts
            
            return []
        except Exception as e:
            self.logger.error(f"Failed to list drafts from account '{account}': {e}")
            return []

    def get_draft(self, draft_id: str, account: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific draft from an account."""
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            
            if hasattr(email_client, 'get_draft'):
                draft = email_client.get_draft(draft_id)
                if isinstance(draft, dict):
                    draft['account'] = account
                    draft['manager'] = 'EmailManager'
                return draft
            else:
                return {'success': False, 'error': 'Get draft not supported', 'account': account}
        except Exception as e:
            return {'success': False, 'error': str(e), 'account': account, 'manager': 'EmailManager'}

    def delete_draft(self, draft_id: str, account: Optional[str] = None) -> Dict[str, Any]:
        """Delete a draft from a specific account."""
        try:
            if account is None:
                account = self.get_default_account()
            
            email_client = self.get_email_client(account)
            
            if hasattr(email_client, 'delete_draft'):
                email_client.delete_draft(draft_id)
                result = {'success': True, 'message': f"Draft {draft_id} deleted successfully"}
            else:
                result = {'success': False, 'error': 'Delete draft not supported'}
            
            result['account'] = account
            result['manager'] = 'EmailManager'
            return result
        except Exception as e:
            return {'success': False, 'error': str(e), 'account': account, 'manager': 'EmailManager'}

    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def clear_cache(self, account: Optional[str] = None) -> None:
        """
        Clear cached information for accounts.
        
        Args:
            account: Specific account to clear cache for (clears all if not specified)
        """
        if account:
            self._account_info_cache.pop(account, None)
        else:
            self._account_info_cache.clear()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all email accounts and their status.
        
        Returns:
            Dict with summary information
        """
        accounts = self.available_accounts
        summary = {
            'total_accounts': len(accounts),
            'available_accounts': accounts,
            'default_account': None,
            'accounts': {}
        }
        
        try:
            summary['default_account'] = self.get_default_account()
        except ValueError:
            pass
        
        # Get basic info for each account
        for account in accounts:
            try:
                config = self.config.get_email_account_config(account)
                summary['accounts'][account] = {
                    'provider': config.provider if config else 'unknown',
                    'display_name': config.display_name if config else '',
                    'enabled': config.enabled if config else False,
                    'is_default': config.default_account if config else False
                }
            except Exception as e:
                summary['accounts'][account] = {
                    'error': str(e),
                    'enabled': False
                }
        
        return summary
