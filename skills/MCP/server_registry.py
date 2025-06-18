"""
JARVERT Master Server Registry

This file contains information about all the specialized MCP servers that make up
the ITS-FRIDAY system. Each server handles a specific domain of functionality
to keep the codebase organized and maintainable.

To run individual servers:
    python weather_server.py
    python email_server.py
    python contacts_server.py
    python browser_server.py
    python google_server.py

Each server runs independently on different ports and can be connected to
separately by MCP clients.
"""

from fastmcp import FastMCP

# Server configurations
SERVERS = {
    "weather": {
        "name": "JARVERT-WEATHER",
        "file": "weather_server.py",
        "description": "Weather information and forecasting tools",
        "tools": [
            "get_weather_now",
            "get_weather_forecast", 
            "get_weather_at"
        ]
    },
    "email": {
        "name": "JARVERT-EMAIL",
        "file": "email_server.py",
        "description": "Email management across multiple accounts",
        "resources": [
            "mcp://friday/email-accounts",
            "mcp://friday/unread-email-counts"
        ],
        "tools": [
            "get_unread_emails_from_account",
            "get_unread_emails_all_accounts",
            "send_email_from_account",
            "list_email_accounts",
            "mark_emails_as_read_tool",
            "mark_emails_as_unread_tool",
            "delete_email_tool",
            "create_draft_tool",
            "update_draft_tool",
            "send_draft_tool",
            "list_drafts_tool",
            "get_draft_tool",
            "delete_draft_tool"
        ]
    },
    "contacts": {
        "name": "JARVERT-CONTACTS",
        "file": "contacts_server.py",
        "description": "Contact management and database operations",
        "tools": [
            "list_contacts",
            "add_contact",
            "update_contact",
            "delete_contact",
            "find_contact",
            "get_contact_by_id"
        ]
    },
    "browser": {
        "name": "JARVERT-BROWSER",
        "file": "browser_server.py",
        "description": "Browser automation and web interaction tools",
        "tools": [
            "browser_navigate_to_url",
            "browser_get_current_page_info",
            "browser_get_page_html",
            "browser_click_element",
            "browser_double_click_element",
            "browser_right_click_element",
            "browser_click_coordinates",
            "browser_type_text",
            "browser_press_key",
            "browser_get_element_text",
            "browser_get_element_attribute",
            "browser_scroll_to_element",
            "browser_scroll_by_pixels",
            "browser_scroll_to_top",
            "browser_scroll_to_bottom",
            "browser_drag_and_drop",
            "browser_drag_by_offset",
            "browser_go_back",
            "browser_go_forward",
            "browser_refresh_page",
            "browser_take_screenshot",
            "browser_execute_javascript",
            "browser_wait_for_element",
            "browser_wait_for_element_clickable",
            "browser_find_elements",
            "browser_close",
            "browser_create_new_session",
            "browser_get_session_status"
        ]
    },
    "google": {
        "name": "JARVERT-GOOGLE",
        "file": "google_server.py",
        "description": "Google services integration (Calendar, Drive)",
        "tools": [
            "get_calendar_events",
            "list_google_drive_files"
        ]
    }
}

def print_server_info():
    """Print information about all available servers."""
    print("ITS-FRIDAY MCP Server Registry")
    print("=" * 50)
    
    for server_key, info in SERVERS.items():
        print(f"\n{info['name']} ({info['file']})")
        print("-" * len(info['name']))
        print(f"Description: {info['description']}")
        
        if 'resources' in info:
            print(f"Resources: {len(info['resources'])}")
            for resource in info['resources']:
                print(f"  - {resource}")
        
        print(f"Tools: {len(info['tools'])}")
        for tool in info['tools'][:5]:  # Show first 5 tools
            print(f"  - {tool}")
        if len(info['tools']) > 5:
            print(f"  ... and {len(info['tools']) - 5} more")

def get_server_by_name(name: str):
    """Get server info by name."""
    for server_key, info in SERVERS.items():
        if info['name'] == name or server_key == name:
            return info
    return None

if __name__ == "__main__":
    print_server_info()
    print("\nTo run a specific server:")
    print("python <server_file>.py")
    print("\nExample:")
    print("python weather_server.py")
