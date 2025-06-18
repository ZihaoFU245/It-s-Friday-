from fastmcp import FastMCP
from typing import Union, Tuple, Dict, Any, Optional, List
import sys
import os

# Add the parent directory to sys.path so we can import from app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import config and configure MCP-specific logging
from app.config import Config
from app import ContactBooklet
config = Config()
config.configure_mcp_logging()

try:
    # Import from specific skill modules for better organization
    from skills.weather_skills import (
        get_weather_now as _get_weather_now,
        get_weather_forecast as _get_weather_forecast,
        get_weather_at as _get_weather_at
    )
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
    from skills.calendar_skills import (
        get_upcoming_events    )
    from skills.drive_skills import (
        list_drive_files
    )
    from skills.use_browser_skills import (
        navigate_to_url,
        get_current_page_info,
        get_page_html,
        click_element,
        double_click_element,
        right_click_element,
        click_coordinates,
        type_text_into_element,
        press_key,
        get_element_text,
        get_element_attribute,
        scroll_to_element,
        scroll_by_pixels,
        scroll_to_top,
        scroll_to_bottom,
        drag_and_drop_elements,
        drag_element_by_offset,
        go_back,
        go_forward,
        refresh_page,
        take_screenshot,        
        execute_javascript,
        wait_for_element,
        wait_for_element_clickable,
        find_elements,
        close_browser,
        create_new_browser_session,
        get_browser_session_status
    )
except ImportError:
    # If running directly, try importing from current directory
    from weather_skills import (
        get_weather_now as _get_weather_now,
        get_weather_forecast as _get_weather_forecast,
        get_weather_at as _get_weather_at
    )
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
        delete_draft    )
    from calendar_skills import (
        get_upcoming_events
    )
    from drive_skills import (
        list_drive_files
    )
    from use_browser_skills import (
        navigate_to_url,
        get_current_page_info,
        get_page_html,
        click_element,
        double_click_element,
        right_click_element,
        click_coordinates,
        type_text_into_element,
        press_key,
        get_element_text,
        get_element_attribute,
        scroll_to_element,
        scroll_by_pixels,
        scroll_to_top,
        scroll_to_bottom,
        drag_and_drop_elements,
        drag_element_by_offset,
        go_back,
        go_forward,
        refresh_page,
        take_screenshot,        execute_javascript,
        wait_for_element,
        wait_for_element_clickable,
        find_elements,
        close_browser,
        create_new_browser_session,
        get_browser_session_status
    )

mcp = FastMCP("ITS-FRIDAY")

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
# WEATHER TOOLS
# ========================================

@mcp.tool()
async def get_weather_now(q: Optional[str] = None, format: Optional[bool] = True) -> Dict[str, Any]:
    """
    Get the current weather for a given place (q), using format can provide you more information,
    but usually formatted information is enough unless being expert

    Args:
        q: Query parameter based on which data is sent back. It could be following:
            * Latitude and Longitude (Decimal degree) e.g: q=48.8567,2.3508
            * city name e.g.: q=Paris
            * US zip e.g.: q=10001
            * UK postcode e.g: q=SW1
            * Canada postal code e.g: q=G2J
            * metar:<metar code> e.g: q=metar:EGLL
            * iata:<3 digit airport code> e.g: q=iata:DXB
            * auto:ip IP lookup e.g: q=auto:ip
            * IP address (IPv4 and IPv6 supported) e.g: q=100.0.0.1

        format: if True, a simpler version will be given

    Returns:
        success: A dictionary contain information key-pair
        failure: A dictionary has key "error" and error information
    """
    return await _get_weather_now(q, format)


@mcp.tool()
async def get_weather_forecast(days: int, q: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the forecast weather for a given place (q) and days ahead.

    Args:
        days: A number between 1 and 14, the num of days to forecast

        q: Query parameter based on which data is sent back. It could be following:
            * Latitude and Longitude (Decimal degree) e.g: q=48.8567,2.3508
            * city name e.g.: q=Paris
            * US zip e.g.: q=10001
            * UK postcode e.g: q=SW1
            * Canada postal code e.g: q=G2J
            * metar:<metar code> e.g: q=metar:EGLL
            * iata:<3 digit airport code> e.g: q=iata:DXB
            * auto:ip IP lookup e.g: q=auto:ip
            * IP address (IPv4 and IPv6 supported) e.g: q=100.0.0.1

    Returns:
        success: A dictionary contain information key-pair
        failure: A dictionary has key "error" and error information
    """
    return await _get_weather_forecast(days, q)

@mcp.tool()
async def get_weather_at(dt: str, q: Optional[str] = None) -> Dict[str, Any]:
    """
    Get weather at a given day, if at past, this will provide weather at every hour interval

    Args:
        dt: In the format of yyyy-MM-dd format and should be after 1st Jan, 2010, and no more than 14 days than present

        q: Query parameter based on which data is sent back. It could be following:
            * Latitude and Longitude (Decimal degree) e.g: q=48.8567,2.3508
            * city name e.g.: q=Paris
            * US zip e.g.: q=10001
            * UK postcode e.g: q=SW1
            * Canada postal code e.g: q=G2J
            * metar:<metar code> e.g: q=metar:EGLL
            * iata:<3 digit airport code> e.g: q=iata:DXB
            * auto:ip IP lookup e.g: q=auto:ip
            * IP address (IPv4 and IPv6 supported) e.g: q=100.0.0.1

    Returns:
        success: A dictionary contain information key-pair
        failure: A dictionary has key "error" and error information
    """
    return await _get_weather_at(dt, q)

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
        Dictionary with deletion result and account information    """
    return delete_draft(draft_id, account)

# ========================================
# CONTACT MANAGEMENT TOOLS
# ========================================

@mcp.tool()
def list_contacts(offset: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
    """
    List all contacts with pagination support.
    
    This tool retrieves contacts from the contact database with support for pagination.
    Use this when you need to browse through all contacts or get a general overview.
    
    Args:
        offset (int, optional): Number of records to skip for pagination. Defaults to 0.
                               Use this to implement pagination (e.g., offset=0 for page 1, 
                               offset=20 for page 2 if limit=20).
        limit (int, optional): Maximum number of records to return. Defaults to 20.
                              Controls the page size. Maximum recommended value is 100.
      Returns:
        List[Dict[str, Any]]: List of contact dictionaries, each containing:
            - id (int): Unique database ID of the contact
            - surname (str): Last name of the contact
            - forename (str): First name of the contact  
            - other_names (List[str]): Additional names (middle names, nicknames, etc.)
            - email (str, optional): Email address
            - phone (str, optional): Phone number
            - address (str, optional): Physical address
            - tags (List[str]): List of tags for categorization (e.g., ['work', 'family'])
            - others (Dict[str, Any]): Additional custom fields as key-value pairs
    
    Example Usage:
        # Get first 20 contacts
        contacts = list_contacts()
        
        # Get contacts 21-40 (page 2)
        contacts = list_contacts(offset=20, limit=20)
        
        # Get just 5 contacts
        contacts = list_contacts(limit=5)
    """
    result = ContactBooklet.load_contacts(offset=offset, limit=limit)
    if result.get('success'):
        return [c.__dict__ for c in result.get('contacts', [])]
    else:
        return {'error': result.get('error', 'Unknown error'), 'manager': result.get('manager', 'ContactBooklet')}

@mcp.tool()
def add_contact(contact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new contact to the database.
    
    This tool creates a new contact record. All contacts must have at least a surname and forename.
    Additional fields are optional but recommended for better contact management.
    
    Args:
        contact (Dict[str, Any]): Contact data dictionary containing:
            - surname (str, required): Last name of the contact
            - forename (str, required): First name of the contact
            - other_names (List[str], optional): Additional names. Defaults to empty list.
            - email (str, optional): Email address. Defaults to None.
            - phone (str, optional): Phone number. Defaults to None.
            - address (str, optional): Physical address. Defaults to None.
            - tags (List[str], optional): Tags for categorization. Defaults to empty list.
            - others (Dict[str, Any], optional): Custom fields. Defaults to empty dict.
    
    Returns:
        Dict[str, Any]: Result dictionary containing:
            - success (bool): Whether the operation succeeded
            - contact_id (int): ID of the newly created contact (if successful)
            - error (str): Error message (if unsuccessful)
            - manager (str): Name of the manager that handled the request
    
    Example Usage:
        # Minimal contact
        result = add_contact({
            "surname": "Doe",
            "forename": "John"
        })
        
        # Full contact with all fields
        result = add_contact({
            "surname": "Smith",
            "forename": "Jane",
            "other_names": ["Marie", "Jay"],
            "email": "jane.smith@email.com",
            "phone": "+1-555-0123",
            "address": "123 Main St, City, State 12345",
            "tags": ["work", "client", "important"],
            "others": {
                "company": "Tech Corp",
                "position": "Developer",
                "birthday": "1990-05-15"
            }
        })
    """
    try:
        from app.modules.contact_booklet import Contact
        c = Contact(**contact)
        return ContactBooklet.add_contact(c)
    except Exception as e:
        return {'success': False, 'error': f'Invalid contact data: {str(e)}', 'manager': 'ContactBooklet'}

@mcp.tool()
def update_contact(contact_id: int, updated: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing contact by ID.
    
    This tool updates a contact's information. The contact is identified by its unique ID.
    All fields in the updated dictionary will replace the existing values.
    
    Args:
        contact_id (int): Unique ID of the contact to update
        updated (Dict[str, Any]): Updated contact data with same structure as add_contact:
            - surname (str, required): Last name of the contact
            - forename (str, required): First name of the contact
            - other_names (List[str], optional): Additional names
            - email (str, optional): Email address
            - phone (str, optional): Phone number
            - address (str, optional): Physical address
            - tags (List[str], optional): Tags for categorization
            - others (Dict[str, Any], optional): Custom fields
    
    Returns:
        Dict[str, Any]: Result dictionary containing:
            - success (bool): Whether the operation succeeded
            - error (str): Error message (if unsuccessful)
            - manager (str): Name of the manager that handled the request
    
    Example Usage:
        # Update email and phone
        result = update_contact(123, {
            "surname": "Doe",
            "forename": "John",
            "email": "john.doe.new@email.com",
            "phone": "+1-555-9999"
        })
        
        # Add tags to existing contact
        result = update_contact(123, {
            "surname": "Smith",
            "forename": "Jane",
            "tags": ["work", "client", "vip"]
        })
    """
    try:
        from app.modules.contact_booklet import Contact
        c = Contact(**updated)
        return ContactBooklet.update_contact(contact_id, c)
    except Exception as e:
        return {'success': False, 'error': f'Invalid contact data: {str(e)}', 'manager': 'ContactBooklet'}

@mcp.tool()
def delete_contact(name: str) -> Dict[str, Any]:
    """
    Delete contacts by name (surname or forename).
    
    This tool deletes all contacts whose surname or forename contains the specified name.
    The search is case-insensitive and supports partial matches.
    
    WARNING: This operation cannot be undone. Be specific with the name to avoid 
    accidentally deleting multiple contacts.
    
    Args:
        name (str): Name to search for deletion. Searches both surname and forename fields.
                   Case-insensitive partial matching is used.
    
    Returns:
        Dict[str, Any]: Result dictionary containing:
            - success (bool): Whether the operation succeeded
            - deleted (int): Number of contacts deleted (if successful)
            - error (str): Error message (if unsuccessful)
            - manager (str): Name of the manager that handled the request
    
    Example Usage:
        # Delete all contacts with "John" in surname or forename
        result = delete_contact("John")
        
        # Delete contacts with "Doe" in surname or forename
        result = delete_contact("Doe")
        
        # More specific search to avoid accidental deletions
        result = delete_contact("John Doe")
    
    Note:
        - Use find_contact first to see what will be deleted
        - Consider using update_contact to modify instead of delete
        - For single contact deletion, use a very specific name
    """
    return ContactBooklet.delete_contact(name)

@mcp.tool()
def find_contact(
    name: str = None, 
    contact_id: int = None, 
    offset: int = 0, 
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Find contacts by name or ID with pagination support.
    
    This is the primary search tool for contacts. You can search by either name or ID.
    The name search is case-insensitive and supports partial matches across both 
    surname and forename fields.
    
    Args:
        name (str, optional): Name to search for. Searches both surname and forename fields.
                             Case-insensitive partial matching is used.
        contact_id (int, optional): Specific contact ID to find. Returns exact match only.
        offset (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 20.
      Returns:
        List[Dict[str, Any]]: List of matching contact dictionaries with same structure as list_contacts.
                             Returns empty list if no matches found.
                             Each contact contains:
            - id (int): Unique database ID of the contact
            - surname (str): Last name
            - forename (str): First name
            - other_names (List[str]): Additional names
            - email (str, optional): Email address
            - phone (str, optional): Phone number
            - address (str, optional): Physical address
            - tags (List[str]): Category tags
            - others (Dict[str, Any]): Custom fields
    
    Example Usage:
        # Search by name (partial match)
        contacts = find_contact(name="John")
        contacts = find_contact(name="Smith")
        contacts = find_contact(name="john doe")  # Case-insensitive
        
        # Search by exact ID
        contacts = find_contact(contact_id=123)
        
        # Search with pagination
        contacts = find_contact(name="John", offset=0, limit=10)
        contacts = find_contact(name="John", offset=10, limit=10)  # Next page
        
        # Get all contacts named "Smith" (no limit)
        contacts = find_contact(name="Smith", limit=100)
    
    Note:
        - Exactly one of 'name' or 'contact_id' must be provided
        - Name search matches both surname and forename
        - ID search returns at most one contact
        - Use this tool before delete_contact to preview what will be deleted
    """
    if name is None and contact_id is None:
        return {'error': 'Either name or contact_id must be provided', 'manager': 'ContactBooklet'}
    
    if name is not None and contact_id is not None:
        return {'error': 'Provide either name or contact_id, not both', 'manager': 'ContactBooklet'}
    
    result = ContactBooklet.find_contact(name=name, contact_id=contact_id, offset=offset, limit=limit)
    if result.get('success'):
        return [c.__dict__ for c in result.get('contacts', [])]
    else:
        return {'error': result.get('error', 'Unknown error'), 'manager': result.get('manager', 'ContactBooklet')}

@mcp.tool()
def get_contact_by_id(contact_id: int) -> Dict[str, Any]:
    """
    Get a single contact by its unique ID.
    
    This tool retrieves a specific contact using its database ID. Use this when you 
    know the exact ID of the contact you want to retrieve.
    
    Args:
        contact_id (int): The unique ID of the contact to retrieve
      Returns:
        Dict[str, Any]: Contact dictionary or error information:
            - If successful: Returns contact dictionary with all fields including 'id' (int)
            - If unsuccessful: Returns error dictionary with 'error' and 'manager' fields
    
    Example Usage:
        # Get contact with ID 123
        contact = get_contact_by_id(123)
        
        # Check if contact was found
        if 'error' not in contact:
            print(f"Found: {contact['forename']} {contact['surname']}")
        else:
            print(f"Error: {contact['error']}")    
    """
    result = ContactBooklet.get_contact_by_id(contact_id)
    if result.get('success'):
        return result.get('contact').__dict__
    else:
        return {'error': result.get('error', 'Unknown error'), 'manager': result.get('manager', 'ContactBooklet')}

# ========================================
# BROWSER AUTOMATION TOOLS
# ========================================

@mcp.tool()
async def browser_navigate_to_url(url: str, headless: bool = True) -> Dict[str, Any]:
    """
    Navigate to a specific URL and return page information.
    
    This creates a new browser session if none exists. If you encounter session errors,
    first use browser_close() to clean up, then browser_create_new_session() to start fresh.
    
    Args:
        url: The URL to navigate to
        headless: Whether to run browser in headless mode (default: True)
        
    Returns:
        Dict containing success status, url, title, page_source, and session information
    """
    return await navigate_to_url(url, headless)

@mcp.tool()
async def browser_get_current_page_info() -> Dict[str, Any]:
    """
    Get information about the current page including URL, title, and HTML length.
    
    Requires an active browser session. If session is invalid, the response will include
    recommendations to use browser_create_new_session() and browser_navigate_to_url().
    
    Returns:
        Dict containing current URL, title, page info, and session status
    """
    return await get_current_page_info()

@mcp.tool()
async def browser_get_page_html() -> Dict[str, Any]:
    """
    Get the full HTML source of the current page.
    
    Returns:
        Dict containing the HTML source and length
    """
    return await get_page_html()

@mcp.tool()
async def browser_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Click on an element specified by selector.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await click_element(selector, by_type, timeout)

@mcp.tool()
async def browser_double_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Double-click on an element.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await double_click_element(selector, by_type, timeout)

@mcp.tool()
async def browser_right_click_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Right-click on an element to open context menu.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await right_click_element(selector, by_type, timeout)

@mcp.tool()
async def browser_click_coordinates(x: int, y: int) -> Dict[str, Any]:
    """
    Click at specific coordinates on the page.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        Dict containing success status and coordinates
    """
    return await click_coordinates(x, y)

@mcp.tool()
async def browser_type_text(selector: str, text: str, by_type: str = "css", 
                           clear_first: bool = True, timeout: int = 10) -> Dict[str, Any]:
    """
    Type text into an input element.
    
    Args:
        selector: The selector string to find the element
        text: Text to type
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        clear_first: Whether to clear the field first
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status and details
    """
    return await type_text_into_element(selector, text, by_type, clear_first, timeout)

@mcp.tool()
async def browser_press_key(key_name: str) -> Dict[str, Any]:
    """
    Press a specific key.
    
    Args:
        key_name: Name of the key ('enter', 'tab', 'escape', 'space', 'backspace', 
                 'delete', 'arrow_up', 'arrow_down', 'arrow_left', 'arrow_right', 
                 'home', 'end', 'page_up', 'page_down', 'f1'-'f5', 'ctrl', 'alt', 'shift')
        
    Returns:
        Dict containing success status
    """
    return await press_key(key_name)

@mcp.tool()
async def browser_get_element_text(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Get text content from an element.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing text content and success status
    """
    return await get_element_text(selector, by_type, timeout)

@mcp.tool()
async def browser_get_element_attribute(selector: str, attribute: str, by_type: str = "css", 
                                      timeout: int = 10) -> Dict[str, Any]:
    """
    Get an attribute value from an element.
    
    Args:
        selector: The selector string to find the element
        attribute: Name of the attribute to get (e.g., 'href', 'src', 'class', 'id')
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing attribute value and success status
    """
    return await get_element_attribute(selector, attribute, by_type, timeout)

@mcp.tool()
async def browser_scroll_to_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Scroll to bring an element into view.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await scroll_to_element(selector, by_type, timeout)

@mcp.tool()
async def browser_scroll_by_pixels(x_pixels: int, y_pixels: int) -> Dict[str, Any]:
    """
    Scroll by specific number of pixels.
    
    Args:
        x_pixels: Horizontal scroll amount (positive = right, negative = left)
        y_pixels: Vertical scroll amount (positive = down, negative = up)
        
    Returns:
        Dict containing success status
    """
    return await scroll_by_pixels(x_pixels, y_pixels)

@mcp.tool()
async def browser_scroll_to_top() -> Dict[str, Any]:
    """
    Scroll to the top of the page.
    
    Returns:
        Dict containing success status
    """
    return await scroll_to_top()

@mcp.tool()
async def browser_scroll_to_bottom() -> Dict[str, Any]:
    """
    Scroll to the bottom of the page.
    
    Returns:
        Dict containing success status
    """
    return await scroll_to_bottom()

@mcp.tool()
async def browser_drag_and_drop(source_selector: str, target_selector: str, 
                               by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Drag an element from source to target.
    
    Args:
        source_selector: Selector for the element to drag
        target_selector: Selector for the drop target
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await drag_and_drop_elements(source_selector, target_selector, by_type, timeout)

@mcp.tool()
async def browser_drag_by_offset(selector: str, x_offset: int, y_offset: int, 
                                by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Drag an element by a specific offset.
    
    Args:
        selector: Selector for the element to drag
        x_offset: Horizontal offset
        y_offset: Vertical offset
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await drag_element_by_offset(selector, x_offset, y_offset, by_type, timeout)

@mcp.tool()
async def browser_go_back() -> Dict[str, Any]:
    """
    Navigate back in browser history.
    
    Returns:
        Dict containing success status
    """
    return await go_back()

@mcp.tool()
async def browser_go_forward() -> Dict[str, Any]:
    """
    Navigate forward in browser history.
    
    Returns:
        Dict containing success status
    """
    return await go_forward()

@mcp.tool()
async def browser_refresh_page() -> Dict[str, Any]:
    """
    Refresh the current page.
    
    Returns:
        Dict containing success status
    """
    return await refresh_page()

@mcp.tool()
async def browser_take_screenshot(filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Take a screenshot of the current page.
    
    Args:
        filename: Optional filename for the screenshot (will auto-generate if not provided)
        
    Returns:
        Dict containing success status and file path
    """
    return await take_screenshot(filename)

@mcp.tool()
async def browser_execute_javascript(script: str) -> Dict[str, Any]:
    """
    Execute JavaScript code on the current page.
    
    Args:
        script: JavaScript code to execute
        
    Returns:
        Dict containing result and success status
    """
    return await execute_javascript(script)

@mcp.tool()
async def browser_wait_for_element(selector: str, by_type: str = "css", timeout: int = 10) -> Dict[str, Any]:
    """
    Wait for an element to appear in the DOM.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await wait_for_element(selector, by_type, timeout)

@mcp.tool()
async def browser_wait_for_element_clickable(selector: str, by_type: str = "css", 
                                            timeout: int = 10) -> Dict[str, Any]:
    """
    Wait for an element to be clickable.
    
    Args:
        selector: The selector string to find the element
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        timeout: Timeout in seconds
        
    Returns:
        Dict containing success status
    """
    return await wait_for_element_clickable(selector, by_type, timeout)

@mcp.tool()
async def browser_find_elements(selector: str, by_type: str = "css") -> Dict[str, Any]:
    """
    Find multiple elements matching the selector and get basic information about them.
    
    Args:
        selector: The selector string to find elements
        by_type: Type of selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
        
    Returns:
        Dict containing element count and basic info about first 5 elements
    """
    return await find_elements(selector, by_type)

@mcp.tool()
async def browser_close() -> Dict[str, Any]:
    """
    Close the browser instance and clean up resources.
    
    Returns:
        Dict containing success status    """
    return await close_browser()

@mcp.tool()
async def browser_create_new_session(headless: bool = True) -> Dict[str, Any]:
    """
    Create a new browser session, replacing any existing session.
    
    This tool creates a fresh browser instance, closing any existing session first.
    Use this when you need to start browser automation or when the current session 
    becomes invalid. After creating a session, use browser_navigate_to_url() to visit a page.
    
    Args:
        headless: Whether to run browser in headless mode (default: True)
        
    Returns:
        Dict containing success status, session info, and next steps
    """
    return await create_new_browser_session(headless)

@mcp.tool()
async def browser_get_session_status() -> Dict[str, Any]:
    """
    Get the current browser session status and information.
    
    This tool checks if there's an active browser session and provides current page
    information if available. Use this to diagnose session issues or check readiness.
    
    Returns:
        Dict containing session status, current URL, title, and recommendations
    """
    return await get_browser_session_status()

if __name__ == "__main__":
    mcp.run()
