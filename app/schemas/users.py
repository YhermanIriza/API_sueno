from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ============================
# 📌 BASE
# ============================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None  # 🔴 Cambiado de "name" a "full_name"
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False


# ============================
# 📌 CREAR USUARIO (registro público)
# ============================

class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="nuevo@correo.com")
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., example="Laura Gómez")  # Recibe "full_name" del frontend
    # 🔴 CORRECCIÓN: role_id ahora es opcional y tiene valor por defecto
    role_id: Optional[int] = Field(default=2, example=2)
    # 🔴 CORRECCIÓN: Se añaden los campos que el formulario de registro envía
    age: int = Field(..., example=30)
    phone: str = Field(..., example="123456789")
    gender: str = Field(..., example="Masculino")
    recaptcha_token: str = Field(..., description="Token de reCAPTCHA para validación")


# ============================
# 📌 ACTUALIZAR USUARIO
# ============================

class UserUpdate(BaseModel):
    full_name: Optional[str] = None  # 🔴 Cambiado de "name" a "full_name"
    password: Optional[str] = Field(None, min_length=6)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    gender: Optional[str] = None


# ============================
# 📌 RESPUESTA (lo que devuelve la API)
# ============================

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None  # 🔴 Cambiado de "name" a "full_name"
    role: str
    is_active: bool
    is_verified: bool
    age: Optional[int] = None
    phone: Optional[str] = None
    gender: Optional[str] = None

    class Config:
        from_attributes = True


# ============================
# 📌 USUARIO PÚBLICO (sin datos sensibles)
# ============================

class PublicUser(BaseModel):
    id: int
    full_name: Optional[str] = None  # 🔴 Cambiado de "name" a "full_name"
    role: str

    class Config:
        from_attributes = True