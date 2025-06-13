import aiohttp
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
    
    async def fetch_weather(self, session: aiohttp.ClientSession, q: str, mode: str = "current", format=True, **extra_params) -> Dict[str, Any]:
        if mode not in ('current', 'forecast', 'search', 'history'):
            raise ValueError("model not supported")
        
        endpoint = f"{self.base_url}/{mode}.json"
        headers = {'Accept': 'application/json'}
        params = {
            "key": self.api_key,
            "q": q,
            "lang": self.lang,
            "aqi": "yes",
            **extra_params
        }
        try:
            async with session.get(endpoint, params=params,
                                   timeout=aiohttp.ClientTimeout(total=self.timeout),
                                   headers=headers) as resp:
                resp.raise_for_status()
                raw = await resp.json()
                
                if format:                    
                    return self._format_normal(raw)
                else:
                    return raw
                
        except asyncio.TimeoutError:
            self.logger.error("Timeout while fetching weather data for city: %s", q)
            return {"error": "Request timed out"}
        
        except aiohttp.ClientError as e:
            self.logger.error("Client error while fetching weather data for city: %s", q)
            return {"error": str(e)}
        
        except json.JSONDecodeError:
            self.logger.error("JSON decode error while fetching weather data for city: %s", q)
            return {"error": "Invalid JSON response"}
        
        except Exception as e:
            self.logger.error("Unexpected error while fetching weather data for city: %s", q)
            return {"error": str(e)}

    def _format_normal(self, raw: Dict[str, Any]) ->Dict[str, Any]:
        current = raw.get('current', {})
        location = raw.get('location', {})
        temp_unit = self.temp_unit.lower()
        temp_key = f'temp_{temp_unit}'
        feelslike_key = f'feelslike_{temp_unit}'

        return {
            "city": location.get('name'),
            "region": location.get('region'),
            "country": location.get('country'),
            "last-updated": current.get('last_updated'),
            "current_weather": current.get('condition', {}).get('text'),
            "temperature": current.get(temp_key, current.get('temp_c')),
            "feels_like": current.get(feelslike_key, current.get('feelslike_c')),
            "humidity": current.get('humidity'),
            "wind_speed": current.get('wind_kph'),
            "wind_direction": current.get('wind_dir'),
            "visibility": current.get("vis_km"),
            "uv": current.get("uv"),
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

    
    async def get_location_by_ip(self, session=None) -> str:
        """
        Asynchronously fetches the user's location based on their IP address using ipinfo.io.
        Returns a coordinate in string.
        
        Args:
            session: An optional aiohttp.ClientSession. If not provided, a new one will be created.
        """
        close_session = False
        headers = {
            'Accept': 'application/json'
        }
        try:
            if session is None:
                session = aiohttp.ClientSession()
                close_session = True

            async with session.get("https://ipinfo.io", timeout=aiohttp.ClientTimeout(total=self.config.timeout), headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("loc", None)
            
        except aiohttp.ClientError as e:
            self.logger.error("Request location HTTP error: %s", str(e))
            return "unknown"
        
        except Exception as e:
            self.logger.error("Unexpected error getting location: %s", str(e))
            return "unknown"
        
        finally:
            if close_session and session is not None:
                await session.close()




