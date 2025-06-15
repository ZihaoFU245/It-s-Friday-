"""
This should use FastAPI to expose key functions to the frontend
"""
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, StringConstraints
from .utils import update_keys
from . import config

# Configure logging for FastAPI application
config.configure_fastapi_logging()

from .dependencies import verify_token
from .routes import weather_endpoints
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_endpoints.router)

class APIKeyRequest(BaseModel):
    key: str = StringConstraints(min_length=1)
    value: str = StringConstraints(min_length=1)


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
    update_keys(request.key, request.value)
    return {"message": f"Key '{request.key}' updated successfully"}




