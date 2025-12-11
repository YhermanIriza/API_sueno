from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# ================================
# 🔐 VARIABLES QUE NECESITA EL SISTEMA
# ================================

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# Security scheme para FastAPI
security = HTTPBearer()


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
        print("❌ Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Token inválido: {e}")
        return None


# ================================
# 🔐 AUTENTICACIÓN - GET CURRENT USER
# ================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Extrae y valida el token JWT del header Authorization.
    Retorna los datos del usuario si el token es válido.
    """
    token = credentials.credentials
    
    print(f"🔍 Token recibido: {token[:30]}...")
    
    # Decodificar el token
    payload = decode_access_token(token)
    
    print(f"🔍 Payload decodificado: {payload}")
    
    if payload is None:
        print("❌ Token inválido o expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer el user_id o email del payload
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    email = payload.get("email")
    
    # 🔧 FIX: Mantener el tipo original del user_id
    # No convertir a string - dejar como viene del token
    
    print(f"🔍 User ID extraído: {user_id} (tipo: {type(user_id)})")
    print(f"🔍 Email extraído: {email}")
    
    if not user_id and not email:
        print("❌ Token no contiene información de usuario válida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene información de usuario válida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Retornar los datos del usuario
    return {
        "id": user_id,
        "email": email,
        **payload
    }


# ================================
# 🔐 OPCIONAL: Verificar roles
# ================================

def require_role(required_role: str):
    """
    Dependency que verifica si el usuario tiene un rol específico.
    """
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "user")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol de {required_role}"
            )
        return current_user
    return role_checker