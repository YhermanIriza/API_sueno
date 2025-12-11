from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.auth import TokenData
from app.db.supabase_client import supabase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


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
        
        # ✅ Obtener user_id desde "sub" (donde lo guardaste en services.py)
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")

        if user_id is None or email is None or role is None:
            print(f"❌ Faltan datos en token: user_id={user_id}, email={email}, role={role}")
            raise credentials_error

        # ✅ CORRECCIÓN: Mantener user_id como string (UUID)
        # NO convertir a int porque es un UUID
        
        print(f"✅ Token decodificado correctamente: user_id={user_id}, email={email}, role={role}")

        return TokenData(id=user_id, email=email, role=role)

    except JWTError as e:
        print(f"❌ Error JWT: {str(e)}")
        raise credentials_error
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        raise credentials_error


def require_role(*roles: str):
    """
    Validar rol requerido.
    Uso: @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    def role_checker(current: TokenData = Depends(get_current_user)):
        if current.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para acceder a este recurso"
            )
        return current

    return role_checker


def get_supabase():
    """
    Devuelve el cliente Supabase.
    """
    return supabase