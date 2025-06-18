from fastmcp import FastMCP
from typing import Dict, Any, List
import sys
import os

# Add the project root directory to sys.path so we can import from app
# Go up two levels: MCP -> skills -> project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import config and configure MCP-specific logging
from app.config import Config
from app import ContactBooklet
config = Config()
config.configure_mcp_logging()

mcp = FastMCP("JARVERT-CONTACTS")

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

if __name__ == "__main__":
    mcp.run()
