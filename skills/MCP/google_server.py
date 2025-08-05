from fastmcp import FastMCP
from typing import Dict, Any
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
    from skills.calendar_skills import (
        get_upcoming_events    
    )
    from skills.drive_skills import (
        list_drive_files
    )
except ImportError:
    # If running directly, try importing from parent skills directory
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from calendar_skills import (
        get_upcoming_events
    )
    from drive_skills import (
        list_drive_files
    )

mcp = FastMCP("JARVERT-GOOGLE")

# ========================================
# GOOGLE SERVICES TOOLS
# ========================================

@mcp.tool()
async def get_calendar_events() -> Dict[str, Any]:
    """
    Get upcoming calendar events from Google Calendar.
    
    Returns:
        Dict containing upcoming events information
    """
    return await get_upcoming_events()

@mcp.tool()
async def list_google_drive_files() -> Dict[str, Any]:
    """
    List files from Google Drive.
    
    Returns:
        Dict containing drive files information
    """
    return await list_drive_files()

if __name__ == "__main__":
    mcp.run()
