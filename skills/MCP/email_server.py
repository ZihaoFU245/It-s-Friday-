from fastmcp import FastMCP
from typing import Union, Dict, Any, Optional, List
import sys
import os

# Add the project root directory to sys.path so we can import from app
# Go up two levels: MCP -> skills -> project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import config and configure MCP-specific logging
from app.config import Config
config = Config()
config.configure_mcp_logging()

try:
    from skills.email_skills import (
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
except ImportError:
    # If running directly, try importing from parent skills directory
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from email_skills import (
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

mcp = FastMCP("JARVERT-EMAIL")

# ========================================
# MCP RESOURCES - Fast, Common Features
# ========================================

@mcp.resource("mcp://friday/email-accounts")
def list_email_accounts_resource() -> str:
    """
    Resource providing information about all configured email accounts.
    This is set as a resource for fast access to account information.
    """
    try:
        account_info = get_email_accounts()
        if account_info.get('success'):
            # Pretty format the account information
            summary = account_info.get('summary', {})
            accounts = account_info.get('accounts', {})
            
            result = f"Email Accounts Summary:\n"
            result += f"Total Accounts: {summary.get('total_accounts', 0)}\n"
            result += f"Default Account: {summary.get('default_account', 'None')}\n\n"
            
            for account_name, details in accounts.items():
                result += f"Account: {account_name}\n"
                result += f"  Provider: {details.get('provider', 'Unknown')}\n"
                result += f"  Display Name: {details.get('display_name', '')}\n"
                result += f"  Enabled: {details.get('enabled', False)}\n"
                result += f"  Is Default: {details.get('is_default', False)}\n"
                if 'error' in details:
                    result += f"  Error: {details['error']}\n"
                result += "\n"
            
            return result
        else:
            return f"Error getting email accounts: {account_info.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error accessing email accounts: {str(e)}"


@mcp.resource("mcp://friday/unread-email-counts")
def unread_email_counts_resource() -> str:
    """
    Resource providing quick access to unread email counts across all accounts.
    This is set as a resource for fast access to common email status information.
    """
    try:
        counts = count_all_unread_emails()
        if counts.get('success'):
            result = "Unread Email Counts:\n\n"
            
            for account, count_data in counts.get('accounts', {}).items():
                if isinstance(count_data, dict):
                    count = count_data.get('count', 0)
                    result += f"{account}: {count} unread emails\n"
                else:
                    result += f"{account}: {count_data} unread emails\n"
            
            total = counts.get('total_count', 0)
            result += f"\nTotal: {total} unread emails across all accounts"
            
            return result
        else:
            return f"Error getting unread counts: {counts.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error accessing unread counts: {str(e)}"

# ========================================
# EMAIL TOOLS
# ========================================

@mcp.tool()
async def get_unread_emails_from_account(
    account: Optional[str] = None,
    max_results: int = 10,
    include_body: bool = False
) -> Dict[str, Any]:
    """
    Get unread emails from a specific email account.

    Args:
        account: Email account name ('personal', 'work', etc.). Uses default account if None.
        max_results: Maximum number of emails to return (default: 10)
        include_body: Whether to include email body content (default: False)

    Returns:
        success: A dictionary with unread emails and account information
        failure: A dictionary with error information
    """
    return await get_unread_emails(account, max_results, include_body)

@mcp.tool()
async def get_unread_emails_all_accounts(max_results_per_account: int = 10) -> Dict[str, Any]:
    """
    Get unread emails from all configured email accounts.

    Args:
        max_results_per_account: Maximum emails per account (default: 10)

    Returns:
        success: A dictionary with unread emails from all accounts
        failure: A dictionary with error information
    """
    return await get_all_unread_emails(max_results_per_account)

@mcp.tool()
async def send_email_from_account(
    to: str,
    subject: str,
    body: str,
    account: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email from a specific account.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        account: Email account to send from (uses default if None)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML email body (optional)

    Returns:
        success: A dictionary with send result and account information
        failure: A dictionary with error information
    """
    # Convert single strings to lists for the function
    to_list = [to] if isinstance(to, str) else to
    cc_list = [cc] if isinstance(cc, str) and cc else None
    bcc_list = [bcc] if isinstance(bcc, str) and bcc else None
    
    return await send_email(
        to=to_list,
        subject=subject,
        body=body,
        account=account,
        cc=cc_list,
        bcc=bcc_list,
        html_body=html_body
    )

@mcp.tool()
def list_email_accounts() -> Dict[str, Any]:
    """
    Get information about all configured email accounts.

    Returns:
        success: A dictionary with account information and summary
        failure: A dictionary with error information
    """
    return get_email_accounts()


# ========================================
# NEW EMAIL TOOLS - Mark as Read/Unread
# ========================================

@mcp.tool()
def mark_emails_as_read_tool(
    message_ids: Union[str, List[str]],
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark message(s) as read in a specific account.

    Args:
        message_ids: Message ID or list of message IDs to mark as read
        account: Email account name (uses default if not specified)

    Returns:
        success: A dictionary with operation result and account information
        failure: A dictionary with error information
    """
    return mark_emails_as_read(message_ids, account)

@mcp.tool()
def mark_emails_as_unread_tool(
    message_ids: Union[str, List[str]],
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark message(s) as unread in a specific account.

    Args:
        message_ids: Message ID or list of message IDs to mark as unread
        account: Email account name (uses default if not specified)

    Returns:
        success: A dictionary with operation result and account information
        failure: A dictionary with error information
    """
    return mark_emails_as_unread(message_ids, account)

@mcp.tool()
def delete_email_tool(
    message_id: str,
    account: Optional[str] = None,
    permanent: bool = False
) -> Dict[str, Any]:
    """
    Delete a message from a specific account.

    Args:
        message_id: Message ID to delete
        account: Email account name (uses default if not specified)
        permanent: Whether to permanently delete (vs move to trash)

    Returns:
        success: A dictionary with operation result and account information
        failure: A dictionary with error information
    """
    return delete_email(message_id, account, permanent)


# ========================================
# NEW EMAIL TOOLS - Draft Management
# ========================================

@mcp.tool()
async def create_draft_tool(
    to: str,
    subject: str,
    body: str,
    account: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a draft message in a specific account.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        account: Email account name (uses default if not specified)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML body (optional)

    Returns:
        success: A dictionary with draft creation result and account information
        failure: A dictionary with error information
    """
    # Convert single strings to lists for the function
    to_list = [to] if isinstance(to, str) else to
    cc_list = [cc] if isinstance(cc, str) and cc else None
    bcc_list = [bcc] if isinstance(bcc, str) and bcc else None
    
    return await create_draft(
        to=to_list,
        subject=subject,
        body=body,
        account=account,
        cc=cc_list,
        bcc=bcc_list,
        html_body=html_body
    )

@mcp.tool()
async def update_draft_tool(
    draft_id: str,
    to: str,
    subject: str,
    body: str,
    account: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing draft in a specific account.

    Args:
        draft_id: ID of the draft to update
        to: Recipient email address
        subject: Email subject
        body: Email body
        account: Email account name (uses default if not specified)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML body (optional)

    Returns:
        success: A dictionary with update result and account information
        failure: A dictionary with error information
    """
    # Convert single strings to lists for the function
    to_list = [to] if isinstance(to, str) else to
    cc_list = [cc] if isinstance(cc, str) and cc else None
    bcc_list = [bcc] if isinstance(bcc, str) and bcc else None
    
    return await update_draft(
        draft_id=draft_id,
        to=to_list,
        subject=subject,
        body=body,
        account=account,
        cc=cc_list,
        bcc=bcc_list,
        html_body=html_body
    )

@mcp.tool()
async def send_draft_tool(
    draft_id: str,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an existing draft from a specific account.

    Args:
        draft_id: ID of the draft to send
        account: Email account name (uses default if not specified)

    Returns:
        success: A dictionary with send result and account information
        failure: A dictionary with error information
    """
    return await send_draft(draft_id, account)

@mcp.tool()
def list_drafts_tool(
    account: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    List drafts from a specific account.

    Args:
        account: Email account name (uses default if not specified)
        max_results: Maximum number of drafts to return

    Returns:
        List of draft objects with account information
    """
    return list_drafts(account, max_results)

@mcp.tool()
def get_draft_tool(
    draft_id: str,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a specific draft from an account.

    Args:
        draft_id: ID of the draft to retrieve
        account: Email account name (uses default if not specified)

    Returns:
        Dictionary with draft information and account details
    """
    return get_draft(draft_id, account)

@mcp.tool()
def delete_draft_tool(
    draft_id: str,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a draft from a specific account.

    Args:
        draft_id: ID of the draft to delete
        account: Email account name (uses default if not specified)

    Returns:
        Dictionary with deletion result and account information
    """
    return delete_draft(draft_id, account)

if __name__ == "__main__":
    mcp.run()
