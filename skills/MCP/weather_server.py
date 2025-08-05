from fastmcp import FastMCP
from typing import Optional, Dict, Any
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
    # Import from specific skill modules for better organization
    from skills.weather_skills import (
        get_weather_now as _get_weather_now,
        get_weather_forecast as _get_weather_forecast,
        get_weather_at as _get_weather_at
    )
except ImportError:
    # If running directly, try importing from parent skills directory
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from weather_skills import (
        get_weather_now as _get_weather_now,
        get_weather_forecast as _get_weather_forecast,
        get_weather_at as _get_weather_at
    )

mcp = FastMCP("JARVERT-WEATHER")

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

if __name__ == "__main__":
    mcp.run()
