from fastapi import APIRouter, Depends, Request
from app.api.services import (
    authenticate_user,
    get_user_by_id,
    list_users,
    create_user,
    update_user,
    delete_user,
    request_password_reset,
    reset_password_with_code
)
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.schemas.users import UserResponse, UserCreate, UserUpdate
from app.api.deps import get_current_user, require_role
from app.core.recaptcha import verify_recaptcha
from app.core.limiter import limiter # 🔴 CORRECCIÓN: Se importa desde el nuevo archivo para evitar el ciclo.

router = APIRouter()

# =======================================================================
print("✅ ARCHIVO DE RUTAS CARGADO CORRECTAMENTE (routes.py)")
# =======================================================================

# ============================
#       AUTH ROUTES
# ============================

@router.post("/auth/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest):
    """
    Login con rate limit y reCAPTCHA.
    Máximo 5 intentos por minuto.
    """
    await verify_recaptcha(data.recaptcha_token)
    return authenticate_user(data)


@router.post("/auth/register", response_model=UserResponse, summary="Registro Público de Usuario")
@limiter.limit("10/minute")
async def public_user_registration(request: Request, data: UserCreate):
    """
    Endpoint público para que cualquier visitante pueda registrarse.
    Rate limit: 10 registros por minuto.
    """
    # ✅ AÑADIDO: Se añade la validación de reCAPTCHA para el registro público.
    await verify_recaptcha(data.recaptcha_token)
    return create_user(data)


@router.post("/auth/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest):
    """
    Solicitar código de recuperación de contraseña.
    Incluye validación de reCAPTCHA y rate limit.
    Se envía un código de 6 caracteres al email.
    Rate limit: 3 intentos por minuto.
    """
    await verify_recaptcha(data.recaptcha_token)
    return request_password_reset(data.email)


@router.post("/auth/reset-password")
@limiter.limit("3/minute")
async def reset_password(request: Request, data: ResetPasswordRequest):
    """
    Restablecer contraseña con código recibido por email.
    Rate limit: 3 intentos por minuto.
    """
    return reset_password_with_code(data.email, data.code, data.new_password)


# ============================
#   USER CRUD (ADMIN ONLY)
# ============================

@router.get("/users", response_model=list[UserResponse])
def get_users(user=Depends(require_role("admin"))):
    return list_users()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, user=Depends(require_role("admin"))):
    return get_user_by_id(user_id)


@router.put("/users/{user_id}", response_model=UserResponse)
def modify_user(user_id: int, data: UserUpdate, user=Depends(require_role("admin"))):
    return update_user(user_id, data)


@router.delete("/users/{user_id}")
def remove_user(user_id: int, user=Depends(require_role("admin"))):
    return delete_user(user_id)


# ============================
#   PROFILE (USER)
# ============================

@router.get("/me", response_model=UserResponse)
def profile(current=Depends(get_current_user)):
    return get_user_by_id(current.id)