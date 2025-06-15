"""
The Blue prints for weather apis
"""
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import verify_token
from pydantic import BaseModel, Field
from typing import Optional

from .. import weather_service

router = APIRouter(
    prefix="/weather",
    tags=["weather"]
)

class ForecastRequest(BaseModel):
    days: int = Field(..., ge=1, le=14)
    q: Optional[str] = None

@router.get('/now')
async def get_weather_now_endpoint(
        q: Optional[str] = None,
        _: None = Depends(verify_token)
    ):
    """Get current weather for a given location"""
    result = await weather_service.get_weather(q, mode="current")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post('/forecast')
async def get_weather_forecast_endpoint(
        request: ForecastRequest,
        _: None = Depends(verify_token)
    ):
    """Get weather forecast for specified days ahead"""
    result = await weather_service.get_forecast(request.days, request.q)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result