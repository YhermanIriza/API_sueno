from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from app.db.supabase_client import supabase
from app.core.config import settings
from app.schemas.users import UserCreate, UserUpdate
from app.schemas.auth import LoginRequest

import secrets
from app.core.email_utils import send_password_reset_email


# ============================
# 📌 Configuración de bcrypt
# ============================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================
# 📌 HASH & VERIFY PASSWORD
# ============================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ============================
# 📌 GENERAR TOKEN JWT
# ============================

def create_access_token(data: dict, expires_minutes: int = 120):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# ============================
# 📌 AUTH SERVICES
# ============================

def authenticate_user(login: LoginRequest):
    """
    Verifica email + contraseña.
    """
    user = supabase.table("users").select("*").eq("email", login.email).maybe_single().execute()

    if not user or not user.data:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    user_data = user.data

    if not verify_password(login.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Obtener rol
    role = supabase.table("roles").select("name").eq("id", user_data["role_id"]).single().execute()

    token = create_access_token({
        "id": user_data["id"],
        "email": user_data["email"],
        "role": role.data["name"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role.data["name"]
    }


# ============================
# 📌 USER SERVICES (CRUD)
# ============================

def get_user_by_id(user_id: int):
    """
    Obtiene un usuario por ID y agrega el nombre del rol.
    """
    result = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_data = result.data
    
    # Obtener el nombre del rol
    role = supabase.table("roles").select("name").eq("id", user_data["role_id"]).single().execute()
    user_data["role"] = role.data["name"] if role.data else "unknown"
    
    return user_data


def list_users():
    """
    Lista todos los usuarios con sus roles.
    """
    result = supabase.table("users").select("*").execute()
    users = result.data
    
    # Agregar el nombre del rol a cada usuario
    for user in users:
        role = supabase.table("roles").select("name").eq("id", user["role_id"]).single().execute()
        user["role"] = role.data["name"] if role.data else "unknown"
    
    return users


def create_user(data: UserCreate):
    """
    Crea un nuevo usuario con role_id = 2 (usuario normal).
    """
    # Verificar si existe
    try:
        existing = supabase.table("users").select("*").eq("email", data.email).maybe_single().execute()
        if existing and existing.data:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Advertencia al verificar email existente: {e}")
    
    hashed = hash_password(data.password)
    
    try:
        # 🔴 CORRECCIÓN CRÍTICA: Usar "full_name" en lugar de "name"
        result = supabase.table("users").insert({
            "email": data.email,
            "hashed_password": hashed,
            "full_name": data.name,  # 🔴 El schema recibe "name" pero la BD espera "full_name"
            "role_id": 2,
            "age": data.age,
            "phone": data.phone,
            "gender": data.gender,
            "is_active": True,
            "is_verified": False
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="No se pudo crear el usuario en la base de datos.")

        user_data = result.data[0]
        
        # Obtener el nombre del rol
        role = supabase.table("roles").select("name").eq("id", user_data["role_id"]).single().execute()
        user_data["role"] = role.data["name"] if role and role.data else "user"
        
        return user_data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")


def update_user(user_id: int, data: UserUpdate):
    """
    Actualiza un usuario existente.
    """
    update_data = data.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    result = supabase.table("users").update(update_data).eq("id", user_id).execute()
    user_data = result.data[0]
    
    # Obtener el nombre del rol
    role = supabase.table("roles").select("name").eq("id", user_data["role_id"]).single().execute()
    user_data["role"] = role.data["name"] if role.data else "unknown"
    
    return user_data


def delete_user(user_id: int):
    """
    Elimina un usuario.
    """
    result = supabase.table("users").delete().eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado correctamente"}


# ============================
# 📌 PASSWORD RECOVERY
# ============================

reset_codes = {}


def request_password_reset(email: str):
    """
    Genera un código de recuperación y lo envía por email.
    """
    user = supabase.table("users").select("*").eq("email", email).maybe_single().execute()
    
    if not user.data:
        raise HTTPException(
            status_code=404, 
            detail="No existe un usuario con ese correo"
        )
    
    reset_code = secrets.token_hex(3).upper()
    
    reset_codes[email] = {
        "code": reset_code,
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }
    
    email_sent = send_password_reset_email(email, reset_code)
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el correo de recuperación"
        )
    
    return {
        "message": "Código de recuperación enviado al correo",
        "email": email
    }


def reset_password_with_code(email: str, code: str, new_password: str):
    """
    Verifica el código y cambia la contraseña.
    """
    if email not in reset_codes:
        raise HTTPException(
            status_code=400,
            detail="No hay ninguna solicitud de recuperación activa"
        )
    
    stored_data = reset_codes[email]
    
    if datetime.utcnow() > stored_data["expires_at"]:
        del reset_codes[email]
        raise HTTPException(
            status_code=400,
            detail="El código ha expirado. Solicita uno nuevo"
        )
    
    if stored_data["code"] != code.upper():
        raise HTTPException(
            status_code=400,
            detail="Código incorrecto"
        )
    
    hashed = hash_password(new_password)
    supabase.table("users").update({
        "hashed_password": hashed
    }).eq("email", email).execute()
    
    del reset_codes[email]
    
    return {
        "message": "Contraseña actualizada correctamente"
    }