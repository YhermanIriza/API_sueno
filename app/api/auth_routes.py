# API_sueno/app/api/auth_routes.py

from fastapi import APIRouter, Depends, Request, HTTPException, status
from typing import Dict, Any
from app.api.services import (
    authenticate_user,
    get_user_by_id,
    list_users,
    create_user,
    update_user,
    delete_user,
    request_password_reset,
    reset_password_with_code,
    hash_password,
    create_access_token
)
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenData
)
from app.schemas.users import UserResponse, UserCreate, UserUpdate
from app.api.deps import get_current_user, require_role
from app.core.recaptcha import verify_recaptcha
from app.core.limiter import limiter
from app.core.database import supabase
from pydantic import BaseModel

router = APIRouter()

print("✅ ARCHIVO DE RUTAS CARGADO CORRECTAMENTE (auth_routes.py)")

# ============================
#       AUTH ROUTES
# ============================

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest):
    """
    Login con rate limit y reCAPTCHA.
    Máximo 5 intentos por minuto.
    Ruta final: POST /api/auth/login
    """
    await verify_recaptcha(data.recaptcha_token)
    return authenticate_user(data)


@router.post("/register", response_model=UserResponse, summary="Registro Público de Usuario")
@limiter.limit("10/minute")
async def public_user_registration(request: Request, data: UserCreate):
    """
    Endpoint público para que cualquier visitante pueda registrarse.
    Rate limit: 10 registros por minuto.
    Ruta final: POST /api/auth/register
    """
    await verify_recaptcha(data.recaptcha_token)
    return create_user(data)


# 🔥 Google Login
class GoogleLoginRequest(BaseModel):
    google_token: str
    email: str
    name: str
    google_id: str


@router.post("/google-login")
async def google_login(data: GoogleLoginRequest):
    """
    Login/registro automático con Google OAuth
    Ruta final: POST /api/auth/google-login
    """
    try:
        print(f"🔍 Google Login - Email: {data.email}, Name: {data.name}")
        
        user_response = None
        try:
            user_response = supabase.table("users").select("*").eq("email", data.email).maybe_single().execute()
            print(f"🔍 Respuesta de Supabase: {user_response}")
        except Exception as db_error:
            print(f"❌ Error al consultar base de datos: {db_error}")
        
        if user_response and user_response.data:
            # Usuario existe
            user_data = user_response.data
            user_id = int(user_data["id"])
            
            print(f"✅ Usuario existente encontrado: {user_id}")
            
            role_response = supabase.table("roles").select("name").eq("id", user_data["role_id"]).single().execute()
            
            token = create_access_token({
                "sub": str(user_id),
                "email": user_data["email"],
                "role": role_response.data["name"],
                "name": data.name
            })
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "role": role_response.data["name"],
                "user": {
                    "id": user_id,
                    "email": user_data["email"],
                    "name": data.name,
                    "role": role_response.data["name"]
                }
            }
        else:
            # Usuario no existe, registrarlo
            print(f"⚠️ Usuario no existe, creando nuevo usuario con Google")
            
            insert_response = supabase.table("users").insert({
                "email": data.email,
                "hashed_password": hash_password(data.google_id),
                "full_name": data.name,
                "role_id": 2,
                "is_active": True,
                "is_verified": True
            }).execute()
            
            if not insert_response.data or len(insert_response.data) == 0:
                raise HTTPException(status_code=500, detail="Error al crear usuario en la base de datos")
            
            user_data = insert_response.data[0]
            user_id = int(user_data["id"])
            
            print(f"✅ Nuevo usuario creado con Google: {user_id}")
            
            # Crear perfil
            try:
                supabase.table("profiles").insert({
                    "id": user_id,
                    "name": data.name,
                }).execute()
                print(f"✅ Perfil creado para Google user: {user_id}")
            except Exception as profile_error:
                print(f"⚠️ Error al crear perfil (no crítico): {profile_error}")
            
            role_response = supabase.table("roles").select("name").eq("id", 2).single().execute()
            
            token = create_access_token({
                "sub": str(user_id),
                "email": data.email,
                "role": role_response.data["name"],
                "name": data.name
            })
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "role": role_response.data["name"],
                "user": {
                    "id": user_id,
                    "email": data.email,
                    "name": data.name,
                    "role": role_response.data["name"]
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en Google login: {e}")
        import traceback
        print(f"❌ Traceback completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error en Google login: {str(e)}")


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest):
    """
    Solicitar código de recuperación de contraseña.
    Ruta final: POST /api/auth/forgot-password
    """
    await verify_recaptcha(data.recaptcha_token)
    return request_password_reset(data.email)


@router.post("/reset-password")
@limiter.limit("3/minute")
async def reset_password(request: Request, data: ResetPasswordRequest):
    """
    Restablecer contraseña con código.
    Ruta final: POST /api/auth/reset-password
    """
    return reset_password_with_code(data.email, data.code, data.new_password)


# ============================
#   USER CRUD (ADMIN ONLY)
# ============================

@router.get("/users", response_model=list[UserResponse])
def get_users(user=Depends(require_role("admin"))):
    """Ruta final: GET /api/auth/users"""
    return list_users()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, user=Depends(require_role("admin"))):
    """Ruta final: GET /api/auth/users/{user_id}"""
    return get_user_by_id(user_id)


@router.put("/users/{user_id}", response_model=UserResponse)
def modify_user(user_id: int, data: UserUpdate, user=Depends(require_role("admin"))):
    """Ruta final: PUT /api/auth/users/{user_id}"""
    return update_user(user_id, data)


@router.delete("/users/{user_id}")
def remove_user(user_id: int, user=Depends(require_role("admin"))):
    """Ruta final: DELETE /api/auth/users/{user_id}"""
    return delete_user(user_id)


# ============================
#   PROFILE (USER)
# ============================

@router.get("/me", response_model=UserResponse)
def profile(current=Depends(get_current_user)):
    """Ruta final: GET /api/auth/me"""
    return get_user_by_id(current.id)


# ============================
#   PROFILE ENDPOINTS
# ============================

class ProfileUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    gender: str | None = None


# 🔧 CORRECCIÓN: Cambiar ruta de /user/profile a /profile
# Para que coincida con el router prefix /api/auth
@router.get("/profile")
async def get_user_profile(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Obtiene el perfil completo del usuario desde Supabase
    Ruta final: GET /api/auth/profile
    ⚠️ NOTA: El frontend debe llamar a /api/auth/profile
    """
    try:
        user_id = int(current_user.id)
        email = current_user.email
        
        print(f"🔍 get_user_profile - user_id: {user_id}, email: {email}")
        
        result = supabase.table("profiles")\
            .select("*")\
            .eq("id", user_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            print(f"✅ Perfil encontrado en Supabase: {result.data[0]}")
            profile_data = result.data[0]
            profile_data["email"] = email
            return profile_data
        else:
            print(f"⚠️ Perfil no encontrado, creando uno básico")
            
            user_result = supabase.table("users")\
                .select("full_name")\
                .eq("id", user_id)\
                .execute()
            
            default_name = user_result.data[0].get("full_name") if user_result.data else email.split("@")[0]
            
            new_profile = supabase.table("profiles").insert({
                "id": user_id,
                "name": default_name,
                "age": None,
                "phone": None,
                "gender": None
            }).execute()
            
            if new_profile.data:
                profile_data = new_profile.data[0]
                profile_data["email"] = email
                return profile_data
            
            return {
                "id": user_id,
                "name": default_name,
                "email": email,
                "age": None,
                "phone": None,
                "gender": None
            }
            
    except Exception as e:
        print(f"❌ Error en get_user_profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener perfil: {str(e)}"
        )


# 🔧 CORRECCIÓN: Cambiar ruta de /user/profile a /profile
@router.put("/profile")
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Actualiza el perfil del usuario en Supabase
    Ruta final: PUT /api/auth/profile
    ⚠️ NOTA: El frontend debe llamar a /api/auth/profile
    """
    try:
        user_id = int(current_user.id)
        email = current_user.email
        
        print(f"🔍 update_user_profile - user_id: {user_id}")
        print(f"🔍 Datos recibidos: {profile_data}")
        
        update_dict = profile_data.dict(exclude_unset=True, exclude_none=True)
        
        print(f"🔍 Datos a actualizar (sin None): {update_dict}")
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar"
            )
        
        existing = supabase.table("profiles")\
            .select("*")\
            .eq("id", user_id)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            print(f"✅ Perfil existe, actualizando...")
            result = supabase.table("profiles")\
                .update(update_dict)\
                .eq("id", user_id)\
                .execute()
        else:
            print(f"⚠️ Perfil no existe, creando uno nuevo...")
            update_dict["id"] = user_id
            result = supabase.table("profiles")\
                .insert(update_dict)\
                .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar perfil en la base de datos"
            )
        
        updated_profile = result.data[0] if result.data else None
        
        if updated_profile:
            updated_profile["email"] = email
        
        print(f"✅ Perfil actualizado correctamente: {updated_profile}")
        
        # 🔧 CORRECCIÓN: Devolver en el formato esperado por el frontend
        return {
            "message": "Perfil actualizado correctamente",
            "data": updated_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al actualizar perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )