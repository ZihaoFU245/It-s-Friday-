"""
This should use FastAPI to expose key functions to the frontend
"""
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from .config import Config, update_keys
from .security import verify_token
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

config = Config()

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