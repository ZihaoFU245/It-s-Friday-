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
        _get_weather_now,
        _get_weather_forecast,
        _get_weather_at,
        get_unread_emails,
        send_email,
        get_upcoming_events,
        list_drive_files
    )
except ImportError:
    # If running directly, try importing from current directory
    from all_skills import (
        _get_weather_now,
        _get_weather_forecast,
        _get_weather_at,
        get_unread_emails,
        send_email,
        get_upcoming_events,
        list_drive_files
    )

mcp = FastMCP("ITS-FRIDAY")

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
    return await _get_weather_forecast(q, days=days)

@mcp.tool()
async def get_weather_at(dt: str, q: Optional[str] = None) -> Dict[str, Any]:
    """
    Get weather at a given day

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
    return await _get_weather_at(dt=dt, q=q)

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
