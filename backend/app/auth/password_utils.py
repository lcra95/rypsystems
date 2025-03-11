# app/auth/password_utils.py
from passlib.context import CryptContext

# Este contexto utilizará bcrypt internamente
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashea la contraseña en texto plano usando bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que la contraseña en texto plano coincida con el hash guardado.
    """
    return pwd_context.verify(plain_password, hashed_password)
