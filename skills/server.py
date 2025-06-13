from fastmcp import FastMCP
from typing import Union, Tuple, Dict, Any, Optional
import sys
import os

# Add the parent directory to sys.path so we can import from app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from skills.all_skills import (
        fetch_weather,
        get_weather_forecast,
        get_unread_emails,
        send_email,
        get_upcoming_events,
        list_drive_files
    )
except ImportError:
    # If running directly, try importing from current directory
    from all_skills import (
        fetch_weather,
        get_weather_forecast,
        get_unread_emails,
        send_email,
        get_upcoming_events,
        list_drive_files
    )

mcp = FastMCP("ITS-FRIDAY")

@mcp.tool()
async def get_weather(city: Optional[str] = None, mode: Optional[str] = "current") -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
    """
    Get the weather condition at a specific city for 4 modes: ['current', 'forecast', 'search', 'history']
    If City is not given, it will use the location in the config file,
    and if in config file it is still not provided, the tool will use User's ip address to find the location, failed if User used a VPN!

    Input:
        - city: Optinal[str, None]
        - mode: Optional
    Return:
        - Success: A tuple with two dictionries, one is formatted, the other is raw (more information)
        - Failed: A tuple with first a string having a failed message and an empty dictionary
    """
    formatted, raw = await fetch_weather(city, mode)
    return formatted, raw

@mcp.tool()
async def get_forecast(city: Optional[str] = None) -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
    """Get weather forecast for a city"""
    return await get_weather_forecast(city)

@mcp.tool()
def check_unread_emails(max_results: int = 10) -> list:
    """Get unread emails from Gmail"""
    return get_unread_emails(max_results)

@mcp.tool()
def send_email_tool(to: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
    """Send an email via Gmail"""
    return send_email(to, subject, body, html_body)

@mcp.tool()
def get_calendar_events(max_results: int = 10) -> list:
    """Get upcoming calendar events"""
    return get_upcoming_events(max_results)

@mcp.tool()
def get_drive_files(page_size: int = 10) -> list:
    """List Google Drive files"""
    return list_drive_files(page_size)

if __name__ == "__main__":
    mcp.run()
