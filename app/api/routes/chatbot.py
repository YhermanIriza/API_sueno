from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.generativeai import configure, GenerativeModel
from app.core.config import settings

router = APIRouter()

# -------------------------
# 1. Validar API Key
# -------------------------
if not settings.GEMINI_API_KEY:
    raise RuntimeError("❌ No se encontró GEMINI_API_KEY en el archivo .env")

# Configurar la API
configure(api_key=settings.GEMINI_API_KEY)

# Modelo Gemini a usar
model = GenerativeModel("gemini-2.5-flash")

# -------------------------
# 2. Esquema de entrada
# -------------------------
class ChatbotRequest(BaseModel):
    prompt: str

# -------------------------
# 3. Endpoint del chatbot
# -------------------------
@router.post("/ask")  # ✅ Sin "/chatbot" porque ya está en el prefix
async def ask_chatbot(data: ChatbotRequest):
    try:
        response = model.generate_content(data.prompt)
        return {"response": response.text}
    except Exception as e:
        print("❌ Error al generar respuesta:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )# Buscar todas las instancias de GenerativeModel
