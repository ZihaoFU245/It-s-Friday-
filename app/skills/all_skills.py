import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from modules import (
    FetchWeather,
    Location,
    GmailClient,
    CalendarClient,
    DriveClient
)
import aiohttp

# Weather stuff
async def fetch_weather(city=None, type_="current"):
    fetcher = FetchWeather()
    config_location = fetcher.config.location

    if city:
        async with aiohttp.ClientSession() as session:
            formatted, original = await fetcher.fetch_weather(session, city, model=type_)
            return formatted, original
    elif config_location:
        async with aiohttp.ClientSession() as session:
            formatted, original = await fetcher.fetch_weather(session, config_location, model=type_)
            return formatted, original
    else:
        location = Location()
        city_country = location.get_location_by_ip()
        if isinstance(city_country, tuple):
            city = city_country[0]
            async with aiohttp.ClientSession() as session:
                formatted, original = await fetcher.fetch_weather(session, city, model=type_)
                return formatted, original
        else:
            # If location lookup failed, return the error
            return city_country, {}



