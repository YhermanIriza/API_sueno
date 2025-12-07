from fastapi import FastAPI
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import os

# Routers
from app.api.routes import router as api_router

# Middlewares
from app.middleware.cors import setup_cors

# Swagger
from app.docs.swagger_config import setup_swagger

# 🔴 CORRECCIÓN: Se importa el limiter desde un archivo centralizado.
from app.core.limiter import limiter

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Backend API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

setup_swagger(app)

setup_cors(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# ================================
# Rutas principales
# ================================
app.include_router(api_router, prefix="/api")

@app.get("/", tags=["Sistema"])
def root():
    # 🔴 CORRECCIÓN: Se devuelve un diccionario de estado válido.
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
    }