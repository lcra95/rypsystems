import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request
from typing import Optional
from .token_manager import validate_and_refresh_token
load_dotenv()
valida_session = os.getenv("ENV_VALIDATION", None)

def get_current_user_id(request: Request) -> int:
    """
    - Lee el header Authorization (Bearer <token>)
    - Valida el token en Redis
    - Retorna el user_id
    """
    if valida_session == "LOCAL":
        return 1
    auth_header: Optional[str] = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )

    token = auth_header.split(" ")[1].strip()
    try:
        user_id = validate_and_refresh_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user_id
