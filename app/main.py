"""
This should use FastAPI to expose key functions to the frontend
"""
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from .config import update_keys
from . import config

# Configure logging for FastAPI application
config.configure_fastapi_logging()

from .security import verify_token
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from . import weather_service, email_service, calendar_service, drive_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class APIKeyRequest(BaseModel):
    key: str
    value: str

class ForecastRequest(BaseModel):
    days: int
    location: Optional[str] = None

@app.get('/')
async def root():
    return HTMLResponse(content=
    """
    <h1>Backend for Friday.</h1>
    """)

@app.post('/set_api_key')
async def set_key(
    request: APIKeyRequest,
    _: None = Depends(verify_token)
):
    if not request.key or not request.value:
        raise HTTPException(status_code=400, detail="Both key and value are required")
    update_keys(request.key, request.value)
    return {"message": f"Key '{request.key}' updated successfully"}


@app.post('/weather')
async def get_weather_endpoint(
    request: ForecastRequest,
    mode: str = "current",
    _: None = Depends(verify_token)
):
    """Get weather using the service layer - generic endpoint"""
    result = await weather_service.get_weather(request.location, mode)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get('/weather/now')
async def get_weather_now_endpoint(
    q: str,
    format: Optional[bool] = True,
    _: None = Depends(verify_token)
):
    """Get current weather for a given location"""
    result = await weather_service.get_weather(q, mode="current", format=format)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post('/weather/forecast')
async def get_weather_forecast_endpoint(
    request: ForecastRequest,
    _: None = Depends(verify_token)
):
    """Get weather forecast for specified days ahead"""
    if request.days < 1 or request.days > 14:
        raise HTTPException(status_code=400, detail="Forecast days must be between 1 and 14")
    
    result = await weather_service.get_forecast(request.days, request.location)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

