from fastapi import FastAPI
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import os

# Cargar variables de entorno primero
load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Backend API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# ✅ CREAR LA INSTANCIA DE FASTAPI UNA SOLA VEZ
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

# ✅ CONFIGURAR SWAGGER, CORS Y RATE LIMITING
from app.docs.swagger_config import setup_swagger
from app.middleware.cors import setup_cors
from app.core.limiter import limiter

setup_swagger(app)
setup_cors(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ✅ IMPORTAR ROUTERS
from app.api.auth_routes import router as auth_router
# from app.api.habits_routes import router as habits_router  # Si tienes otros routers
# from app.api.achievements_routes import router as achievements_router

# ✅ REGISTRAR ROUTERS DIRECTAMENTE (SIN ROUTER INTERMEDIO)
# Esto hace que las rutas sean: /api/auth/login, /api/auth/register, etc.
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# ✅ Si tienes otros routers, regístralos aquí también
# app.include_router(habits_router, prefix="/api/habits", tags=["Habits"])
# app.include_router(achievements_router, prefix="/api/achievements", tags=["Achievements"])

# ✅ RUTA RAÍZ
@app.get("/", tags=["Sistema"])
def root():
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "status": "running"
    }

@app.get("/health", tags=["Sistema"])
def health_check():
    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "version": APP_VERSION
    }


# 🔍 DEBUG: Imprimir todas las rutas registradas (puedes comentar esto después)
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🚀 RUTAS REGISTRADAS EN LA API:")
    print("="*60)
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"  {methods:10} -> {route.path}")
    print("="*60 + "\n")