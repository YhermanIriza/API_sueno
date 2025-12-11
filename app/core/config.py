from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Mi API Backend"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT
    SECRET_KEY: str = Field(default="CAMBIA_ESTE_SECRET_SUPER_SEGURO")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Recovery Password
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 10

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_ANON_KEY: str

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://tudominio.com"
    ]

    # Email
    EMAIL_FROM: str
    EMAIL_PASSWORD: str
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_FROM_NAME: str = "Soporte - Mi API Backend"

    # reCAPTCHA
    RECAPTCHA_SECRET_KEY: str = Field(default="")

    # Seeds
    RUN_SEED_ON_STARTUP: bool = False

    # ⭐⭐⭐ ChatBot API Key – CORREGIDA ⭐⭐⭐
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# ✅ Instancia global de settings
settings = Settings()