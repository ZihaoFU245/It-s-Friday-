"""
Email Skills Module

This module provides email-related functionality using EmailManager
for multi-account email support. All operations are provider-agnostic
and work with any configured email accounts.
"""

from app import email_manager
from typing import Optional, Union, Dict, Any, List


async def get_unread_emails(
    account: Optional[str] = None,
    max_results: int = 10,
    include_body: bool = False
) -> Dict[str, Any]:
    """
    Get unread emails from a specific account or default account.
    
    Args:
        account: Email account name ('personal', 'work', etc.). Uses default if None.
        max_results: Maximum number of emails to return (default: 10)
        include_body: Whether to include email body content (default: False)
        
    Returns:
        Dict with success status and list of unread emails
    """
    try:
        messages = email_manager.get_unread_messages(
            account=account,
            max_results=max_results,
            include_body=include_body
        )
        
        return {
            'success': True,
            'account': account or email_manager.get_default_account(),
            'count': len(messages),
            'messages': messages,
            'service': 'EmailManager'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'account': account,
            'service': 'EmailManager'
        }


async def get_all_unread_emails(max_results_per_account: int = 10) -> Dict[str, Any]:
    """
    Get unread emails from all configured email accounts.
    
    Args:
        max_results_per_account: Maximum emails per account (default: 10)
        
    Returns:
        Dict with unread emails from all accounts
    """
    try:
        all_messages = email_manager.get_all_unread_messages(max_results_per_account)
        
        total_count = sum(len(messages) for messages in all_messages.values())
        
        return {
            'success': True,
            'total_count': total_count,
            'accounts': all_messages,
            'service': 'EmailManager'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'service': 'EmailManager'
        }


async def send_email(
    to: Union[str, List[str]],
    subject: str,
    body: str,
    account: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    html_body: Optional[str] = None,
    attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Send email from a specific account.
    
    Args:
        to: Recipient email address(es)
        subject: Email subject
        body: Email body text
        account: Email account to send from (uses default if None)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML email body (optional)
        attachments: List of file paths to attach (optional)
        
    Returns:
        Dict with send result and account information
    """
    return await email_manager.send_email(
        to=to,
        subject=subject,
        body=body,
        account=account,
        cc=cc,
        bcc=bcc,
        html_body=html_body,
        attachments=attachments
    )


def count_unread_emails(account: Optional[str] = None) -> Dict[str, Any]:
    """
    Count unread emails in a specific account.
    
    Args:
        account: Email account name (uses default if None)
        
    Returns:
        Dict with unread count and account information
    """
    return email_manager.count_unread_messages(account)


def count_all_unread_emails() -> Dict[str, Any]:
    """
    Count unread emails across all configured accounts.
    
    Returns:
        Dict with unread counts for all accounts
    """
    return email_manager.count_all_unread_messages()


def get_email_accounts() -> Dict[str, Any]:
    """
    Get information about all configured email accounts.
    
    Returns:
        Dict with account information and summary
    """
    try:
        summary = email_manager.get_summary()
        account_info = email_manager.get_all_account_info()
        
        return {
            'success': True,
            'summary': summary,
            'accounts': account_info,
            'service': 'EmailManager'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'service': 'EmailManager'
        }


# New functions for mark as read/unread
def mark_emails_as_read(
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
    return email_manager.mark_as_read(message_ids, account)


def mark_emails_as_unread(
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
    return email_manager.mark_as_unread(message_ids, account)


def delete_email(
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
    return email_manager.delete_message(message_id, account, permanent)


# Draft management functions
async def create_draft(
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
    return await email_manager.create_draft(
        to=to,
        subject=subject,
        body=body,
        account=account,
        cc=cc,
        bcc=bcc,
        html_body=html_body,
        attachments=attachments
    )


async def update_draft(
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
    """
    Update an existing draft in a specific account.
    
    Args:
        draft_id: ID of the draft to update
        to: Recipient email address(es)
        subject: Email subject
        body: Email body
        account: Account name (uses default if not specified)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML body (optional)
        attachments: File attachments (optional)
        
    Returns:
        Dict with update result and account information
    """
    return await email_manager.update_draft(
        draft_id=draft_id,
        to=to,
        subject=subject,
        body=body,
        account=account,
        cc=cc,
        bcc=bcc,
        html_body=html_body,
        attachments=attachments
    )


async def send_draft(
    draft_id: str,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an existing draft from a specific account.
    
    Args:
        draft_id: ID of the draft to send
        account: Account name (uses default if not specified)
        
    Returns:
        Dict with send result and account information
    """
    return await email_manager.send_draft(draft_id, account)


def list_drafts(
    account: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    List drafts from a specific account.
    
    Args:
        account: Account name (uses default if not specified)
        max_results: Maximum number of drafts to return
        
    Returns:
        List of draft objects with account information
    """
    return email_manager.list_drafts(account, max_results)


def get_draft(
    draft_id: str,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a specific draft from an account.
    
    Args:
        draft_id: ID of the draft to retrieve
        account: Account name (uses default if not specified)
        
    Returns:
        Dict with draft information and account details
    """
    return email_manager.get_draft(draft_id, account)


def delete_draft(
    draft_id: str,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a draft from a specific account.
    
    Args:
        draft_id: ID of the draft to delete
        account: Account name (uses default if not specified)
        
    Returns:
        Dict with deletion result and account information
    """
    return email_manager.delete_draft(draft_id, account)
