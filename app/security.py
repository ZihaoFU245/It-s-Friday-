from typing import Optional
from fastapi import HTTPException, Header
from .config import Config

config = Config()
API_TOKEN = config.security_key or "you-will-never-guess"

def verify_token(authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

def get_current_token() -> str:
    return API_TOKEN
