"""
Weather Service - High-level weather operations

This service abstracts weather operations and provides a stable API
regardless of the underlying weather provider (OpenWeatherMap, etc.)
"""

from typing import Optional, Tuple, Dict, Any, Union
import aiohttp
from ..modules.weather import FetchWeather, Location


class WeatherService:
    """
    High-level weather service that abstracts weather operations.
    
    Features:
    - Automatic location detection (config -> IP lookup)
    - Multiple weather modes (current, forecast, history, search)
    - Consistent error handling
    - Provider-agnostic interface
    """
    
    def __init__(self, config):
        self.config = config
        self._weather_fetcher = None
        self._location_service = None
    
    @property
    def weather_fetcher(self) -> FetchWeather:
        """Lazy initialization of weather fetcher"""
        if self._weather_fetcher is None:
            self._weather_fetcher = FetchWeather()
        return self._weather_fetcher
    
    @property 
    def location_service(self) -> Location:
        """Lazy initialization of location service"""
        if self._location_service is None:
            self._location_service = Location()
        return self._location_service
    
    async def get_weather(
        self, 
        q: Optional[str] = None, 
        mode: str = "current",
        format: bool = True,
        **others: Any
    ) -> Dict[str, Any]:
        """
        Get weather data with smart location resolution.
        
        Args:
            q: search query. see "https://www.weatherapi.com/docs/" If None, uses config location or IP lookup
            mode: Weather mode - 'current', 'forecast', 'search', 'history'; forecast and history need additional params
            
        Returns:
            Success: A dictionary of returned weather information
            Error: A dictionary {"error": ${error message}}
        """
        try:
            # Determine location
            target = await self._resolve_location(q)
            if target == "unknown":
                return {"error": "Location can not be determined"}
            
            # Fetch weather data
            async with aiohttp.ClientSession() as session:
                info = await self.weather_fetcher.fetch_weather(
                    session, target, mode, format, **others
                )
                return info
                
        except Exception as e:
            error_msg = f"Weather service error: {str(e)}"
            return {"error": error_msg}
    
    async def _resolve_location(self, q: Optional[str]) -> str:
        """
        Resolve the target location using priority: provided -> config -> IP lookup
        
        Returns:
            coordinate as a string
        """
        # 1. Use provided location if available
        if q:
            return q
        
        # 2. Use config location if available  
        config_location = self.config.location
        if config_location:
            return config_location
        
        # 3. Fallback to IP-based location detection
        coordinates = await self.location_service.get_location_by_ip()
        return coordinates
    
    async def weather_at(self, timestamp, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Search Weather at a given day
        
        Args:
            A time Stamp in format yyyy-MM-dd
        """
        return await self.get_weather(query, "history", dt=timestamp)
    
    async def get_forecast(self, days: int, query: Optional[str] = None) -> Dict[str, Any]:
        """Get weather forecast, format is set to True"""
        if days < 1 or days > 14:
            return {"error": "Forecast days must be in a proper range, 1 - 14"}
        return await self.get_weather(query, "forecast", days=days)
    

