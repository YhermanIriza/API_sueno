from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt

from app.core.config import settings


# ================================
# 🔐 VARIABLES QUE NECESITA EL SISTEMA
# ================================

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


# ================================
# 🔐 HASHING PASSWORDS (bcrypt)
# ================================

def hash_password(password: str) -> str:
    """Genera un hash seguro usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ================================
# 🔑 JWT TOKEN GENERATION
# ================================

def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Crea un JWT válido por X minutos."""
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica un JWT y retorna los datos internos."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
