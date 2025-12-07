import re
import uuid
from datetime import datetime
from typing import Optional


# -----------------------------------------
# 🔧 GENERIC UTILS
# -----------------------------------------
def generate_uuid() -> str:
    """Genera un UUID único para IDs."""
    return str(uuid.uuid4())


def current_timestamp() -> str:
    """Retorna la fecha/hora actual en formato ISO."""
    return datetime.utcnow().isoformat()


# -----------------------------------------
# 🧼 STRING CLEANING
# -----------------------------------------
def normalize_string(value: str) -> str:
    """Limpia espacios y convierte a formato estándar."""
    return value.strip().lower()


def sanitize_text(value: str) -> str:
    """Elimina caracteres peligrosos."""
    return re.sub(r"[<>\"']", "", value)


# -----------------------------------------
# 📧 EMAIL VALIDATION
# -----------------------------------------
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


def is_valid_email(email: str) -> bool:
    """Valida que un email tenga un formato correcto."""
    return bool(re.match(EMAIL_REGEX, email))


# -----------------------------------------
# 🔐 PASSWORD UTILS
# -----------------------------------------
def is_strong_password(password: str) -> bool:
    """
    Verifica que una contraseña sea segura.
    Requisitos:
    - mínimo 8 caracteres
    - 1 mayúscula
    - 1 minúscula
    - 1 número
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True
