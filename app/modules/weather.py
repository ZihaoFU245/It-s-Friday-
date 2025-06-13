import os
import sys
import aiohttp
import requests
import asyncio
import json
from typing import Any, Dict, Tuple
import logging
from .. import config

class FetchWeather:
    base_url: str
    api_key: str
    lang: str
    temp_unit: str
    timeout: int
    logger: Any

    def __init__(self):
        self.config = config
        self.logger = logging.getLogger(__name__)
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
            self.logger.error("Timeout while fetching weather data for city: %s", city)
            return {"error": "Request timed out"}, {}
        except aiohttp.ClientError as e:
            self.logger.error("Client error while fetching weather data for city: %s", city)
            return {"error": str(e)}, {}
        except json.JSONDecodeError:
            self.logger.error("JSON decode error while fetching weather data for city: %s", city)
            return {"error": "Invalid JSON response"}, {}
        except Exception as e:
            self.logger.error("Unexpected error while fetching weather data for city: %s", city)
            return {"error": str(e)}, {}
        
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
    
class Location:
    def __init__(self):
        self.config = config
        self.logger = logging.getLogger(__name__)

    
    def get_location_by_ip(self):
        """
        Asynchronously fetches the user's location based on their IP address using ipinfo.io.
        Returns a tuple (city, country) or a dict with error info.
        """
        try:
            resp = requests.get("https://ipinfo.io")
            data = resp.json()
            return data.get('city', None), data.get('country', None)
        except requests.HTTPError as e:
            self.logger.error("Request location HTTP error", e)
            return "getting location by ip failed"


if __name__ == "__main__":
    import asyncio
    import aiohttp

    async def test_weather():
        city = "madrid"
        fetcher = FetchWeather()
        async with aiohttp.ClientSession() as session:
            formatted, original = await fetcher.fetch_weather(session, city, model="current")
            print("Weather API Test for city 'madrid':")
            print("Formatted response:")
            print(formatted)
            print("\nOriginal response:")
            print(original)
            print("\n---\n")

    def test_location():
        location = Location()
        result =  location.get_location_by_ip()
        print("Location by IP Test:")
        print(result)
        print("\n---\n")

    test_location()

