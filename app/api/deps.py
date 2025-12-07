from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
# 🔴 CORRECCIÓN: Eliminado "API_sueno." del inicio de la importación
from app.schemas.auth import TokenData
from app.db.supabase_client import supabase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================
# 📌 Obtener datos del token
# ============================

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Decodifica el JWT y devuelve información del usuario.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: int = payload.get("id")
        email: str = payload.get("email")
        role: str = payload.get("role")

        if user_id is None or email is None or role is None:
            raise credentials_error

        return TokenData(id=user_id, email=email, role=role)

    except JWTError:
        raise credentials_error


# ============================
# 📌 Validar rol requerido
# ============================

def require_role(*roles: str):
    """
    Uso en rutas:
        @router.get("/admin")
        def admin_route(user = Depends(require_role("admin"))):
            ...
    """

    def role_checker(current: TokenData = Depends(get_current_user)):
        if current.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para acceder a este recurso"
            )
        return current

    return role_checker


# ============================
# 📌 Obtener cliente Supabase
# ============================

def get_supabase():
    """
    Devuelve el cliente Supabase para usar en servicios y rutas.
    """
    return supabase