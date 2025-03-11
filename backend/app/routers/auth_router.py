from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from pydantic import BaseModel
from app.models.user import User
from app.auth.token_manager import create_session_token

router = APIRouter(prefix="/auth", tags=["authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Verifica email y password, si es correcto, genera token de sesión en Redis.
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Aquí deberías comparar contraseñas con hashing (bcrypt, passlib, etc.)
    if user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generamos token de sesión
    token = create_session_token(user.id)

    return LoginResponse(token=token)
