import secrets
from .redis_conn import redis_client

TOKEN_EXPIRATION_SECONDS = 3600  # 1 hora

def create_session_token(user_id: int) -> str:
    """
    Genera un token aleatorio y lo guarda en Redis con TTL de 1 hora
    """
    token = secrets.token_urlsafe(32)  # Cadena aleatoria segura
    redis_client.setex(
        name=f"session:{token}",
        time=TOKEN_EXPIRATION_SECONDS,
        value=user_id
    )
    return token

def validate_and_refresh_token(token: str) -> int:
    """
    Verifica el token en Redis:
      - Si existe, renueva su TTL (1 hora).
      - Retorna el user_id asociado.
      - Si no existe, lanza excepción.
    """
    key = f"session:{token}"
    user_id = redis_client.get(key)
    if user_id is None:
        # Significa que el token no existe o expiró
        raise ValueError("Invalid or expired token")

    # Si existe, refrescamos la expiración
    redis_client.expire(key, TOKEN_EXPIRATION_SECONDS)
    return int(user_id)
