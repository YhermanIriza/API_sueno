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
    name: str = Field(..., example="Juan Pérez")
    role_id: int = Field(..., example=2)
    recaptcha_token: str = Field(..., description="Token de reCAPTCHA v2")


class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
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
    id: int
    email: EmailStr
    role: str