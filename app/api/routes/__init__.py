from fastapi import APIRouter

# Crear router general
router = APIRouter()

# ============================
# IMPORTAR TODAS LAS RUTAS
# ============================

# Rutas de autenticación (del archivo auth_routes.py)
from app.api.auth_routes import router as auth_router

# Nueva ruta del ChatBot
from .chatbot import router as chatbot_router

# ============================
# REGISTRAR RUTAS
# ============================

# ✅ Registrar todas las rutas de autenticación y usuarios
router.include_router(auth_router, tags=["Auth & Users"])

# ✅ Registrar chatbot
router.include_router(chatbot_router, prefix="/chatbot", tags=["ChatBot"])