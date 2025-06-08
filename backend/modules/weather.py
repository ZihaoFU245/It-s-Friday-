import os
import aiohttp
import asyncio
import json
from typing import Any, Dict, Tuple
from ..config import Config

class FetchWeather:
    config: Config
    base_url: str
    api_key: str
    lang: str
    temp_unit: str
    timeout: int

    def __init__(self):
        self.config = Config()
        self.base_url = self.config.weather_url
        self.api_key = self.config.weather_api_key
        self.lang = self.config.lang
        self.temp_unit = self.config.temp_unit
        self.timeout = self.config.timeout

        if not self.api_key:
            raise ValueError("api key was Not Found")
        if not self.base_url:
            raise ValueError("Weather base url is not provided")
        
    async def fetch_weather(
        self,
        session: aiohttp.ClientSession,
        city: str,
        model: str = "current",
        **extra_params
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        model: one of 'current', 'forecast', 'search', 'history', etc.
        """
        endpoint = f"{self.base_url}/{model}.json"
        params = {
            'key': self.api_key,
            'q': city,
            'lang': self.lang,
            'aqi': 'yes',
            **extra_params
        }
        try:
            async with session.get(
                endpoint,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                formatted = self._format_response(data)
                return formatted, data
                
        except asyncio.TimeoutError:
            return {"error": "Request timed out"}, {}
        except aiohttp.ClientError as e:
            return {"error": str(e)}, {}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}, {}
        
    def _format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        current = data.get('current', {})
        location = data.get('location', {})
        temp_unit = self.temp_unit.lower()
        temp_key = f'temp_{temp_unit}'
        feelslike_key = f'feelslike_{temp_unit}'

        return {
            "city": location.get('name'),
            "region": location.get('region'),
            "country": location.get('country'),
            "current_weather": current.get('condition', {}).get('text'),
            "temperature": current.get(temp_key, current.get('temp_c')),
            "feels_like": current.get(feelslike_key, current.get('feelslike_c')),
            "humidity": current.get('humidity'),
            "wind_speed": current.get('wind_kph'),
            "wind_direction": current.get('wind_dir'),
            "air_quality": self._format_air_quality(current.get('air_quality', {})),
            "unit": f"°{temp_unit.upper()}"
        }

    def _format_air_quality(self, air_quality: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "pm2_5": air_quality.get("pm2_5"),
            "pm10": air_quality.get("pm10")
        }
    
"""
if __name__ == "__main__":
    import asyncio
    import aiohttp

    async def test_weather():
        city = "madrid"
        fetcher = FetchWeather()
        async with aiohttp.ClientSession() as session:
            formatted, original = await fetcher.fetch_weather(session, city, model="current")
            return formatted, original

    result = asyncio.run(test_weather())
    formatted, original = result
    print("Formatted response:")
    print(formatted)
    print("\nOriginal response:")
    print(original)
"""