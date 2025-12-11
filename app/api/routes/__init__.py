from fastapi import APIRouter

# Crear router general
router = APIRouter()

# ============================
# IMPORTAR TODAS LAS RUTAS
# ============================

# Rutas de autenticación (del archivo auth_routes.py)
from app.api.auth_routes import router as auth_router

# Ruta del ChatBot
from .chatbot import router as chatbot_router

# Rutas de hábitos
from app.api.habits.routes import router as habits_router

# Rutas de achievements
from app.api.achievements.routes import router as achievements_router

# ============================
# REGISTRAR RUTAS
# ============================

# ✅ Registrar todas las rutas de autenticación y usuarios
router.include_router(auth_router, tags=["Auth & Users"])

# ✅ Registrar chatbot
router.include_router(chatbot_router, prefix="/chatbot", tags=["ChatBot"])

# ✅ Registrar hábitos (SIN prefix adicional - ya viene de main.py)
router.include_router(habits_router, tags=["Habits"])

# ✅ Registrar achievements (SIN prefix adicional - ya viene de main.py)
router.include_router(achievements_router, tags=["Achievements"])