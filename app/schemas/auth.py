from pydantic import BaseModel, EmailStr, Field


# ============================
# 📌 AUTH: LOGIN
# ============================

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="usuario@example.com")
    password: str = Field(..., min_length=6, example="123456")
    recaptcha_token: str = Field(..., description="Token de reCAPTCHA v2")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# ============================
# 📌 AUTH: REGISTRO
# ============================

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., example="nuevo@correo.com")
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., example="Juan Pérez")
    age: int = Field(..., example=30)
    phone: str = Field(..., example="123456789")
    gender: str = Field(..., example="Masculino")
    recaptcha_token: str = Field(..., description="Token de reCAPTCHA v2")
    role_id: int = Field(default=2, example=2)


class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    message: str = "Usuario registrado correctamente"


# ============================
# 📌 AUTH: RECUPERAR CONTRASEÑA
# ============================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    recaptcha_token: str = Field(..., description="Token de reCAPTCHA v2")


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="Código de 6 caracteres")
    new_password: str = Field(..., min_length=6)


# ============================
# 📌 TOKEN RESPONSE
# ============================

class TokenData(BaseModel):
    id: str  # ✅ CAMBIADO: Ahora es string (UUID)
    email: EmailStr
    role: str