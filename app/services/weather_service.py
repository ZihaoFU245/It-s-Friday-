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
        city: Optional[str] = None, 
        mode: str = "current"
    ) -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
        """
        Get weather data with smart location resolution.
        
        Args:
            city: Optional city name. If None, uses config location or IP lookup
            mode: Weather mode - 'current', 'forecast', 'search', 'history'
            
        Returns:
            Success: Tuple of (formatted_data, raw_data)
            Error: Tuple of (error_message, empty_dict)
        """
        try:
            # Determine location
            target_city = await self._resolve_location(city)
            if isinstance(target_city, tuple) and len(target_city) == 2 and isinstance(target_city[1], dict):
                # Error from location resolution
                return target_city
            
            # Fetch weather data
            async with aiohttp.ClientSession() as session:
                formatted, raw = await self.weather_fetcher.fetch_weather(
                    session, target_city, model=mode
                )
                return formatted, raw
                
        except Exception as e:
            error_msg = f"Weather service error: {str(e)}"
            return error_msg, {}
    
    async def _resolve_location(self, city: Optional[str]) -> Union[str, Tuple[str, Dict]]:
        """
        Resolve the target location using priority: provided -> config -> IP lookup
        
        Returns:
            Success: city name as string
            Error: tuple of (error_message, empty_dict)
        """
        # 1. Use provided city if available
        if city:
            return city
        
        # 2. Use config location if available  
        config_location = self.config.location
        if config_location:
            return config_location
        
        # 3. Fallback to IP-based location detection
        try:
            city_country = self.location_service.get_location_by_ip()
            if isinstance(city_country, tuple) and len(city_country) >= 2:
                return city_country[0]  # Return city name
            else:
                # Location lookup failed
                return "Failed to determine location. Please specify a city.", {}
        except Exception as e:
            return f"Location detection error: {str(e)}", {}
    
    async def search_location(self, query: str) -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
        """Search for location information"""
        return await self.get_weather(city=query, mode="search")
    
    async def get_forecast(self, city: Optional[str] = None) -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
        """Get weather forecast"""
        return await self.get_weather(city=city, mode="forecast")
    
    async def get_current(self, city: Optional[str] = None) -> Union[Tuple[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict]]:
        """Get current weather"""
        return await self.get_weather(city=city, mode="current")
