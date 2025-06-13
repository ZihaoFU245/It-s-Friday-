"""
This should use FastAPI to expose key functions to the frontend
"""
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from .config import update_keys
from . import config
from .security import verify_token
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from . import weather_service, email_service

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


@app.get('/weather')
async def get_weather_endpoint(
    city: Optional[str] = None,
    mode: str = "current",
    _: None = Depends(verify_token)
):
    """Get weather using the service layer"""
    formatted, raw = await weather_service.get_weather(city, mode)
    if isinstance(formatted, str):  # Error case
        raise HTTPException(status_code=400, detail=formatted)
    return {"formatted": formatted, "raw": raw}

@app.get('/emails/unread')
async def get_unread_emails_endpoint(
    max_results: int = 10,
    _: None = Depends(verify_token)
):
    """Get unread emails using the service layer"""
    emails = email_service.get_unread_messages(max_results)
    return {"emails": emails}