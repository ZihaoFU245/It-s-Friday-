"""
Weather Skills Module

This module provides weather-related functionality using the service layer.
All weather operations are provider-agnostic and use the weather service.
"""

from app import weather_service
from typing import Optional, Dict, Any


async def get_weather_now(
    q: Optional[str] = None, 
    format: Optional[bool] = True,
) -> Dict[str, Any]:
    """
    Fetch current weather using the weather service.
    Provider-agnostic with better error handling.
    
    Args:
        q: Location query (city, coordinates, etc.)
        format: Whether to format the response for better readability
        
    Returns:
        Dict with weather information
    """
    return await weather_service.get_weather(q=q, format=format)


async def get_weather_forecast(
    days: int,
    q: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get weather forecast using service layer.
    
    Args:
        days: Number of days to forecast (1-14)
        q: Location query (city, coordinates, etc.)
        
    Returns:
        Dict with forecast information
    """
    return await weather_service.get_forecast(days, q)


async def get_weather_at(
    dt: str,
    q: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get weather at a specific time stamp.
    
    Args:
        dt: Date in yyyy-MM-dd format
        q: Location query (city, coordinates, etc.)
        
    Returns:
        Dict with weather information for the specified date
    """
    return await weather_service.weather_at(dt, q)
