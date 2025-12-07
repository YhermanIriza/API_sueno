import os
import google.generativeai as genai
from dotenv import load_dotenv

class ChatBotService:

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("AIzaSyBODrBeEqyqrrNtZm0KfvZ7vqZqAun9VOM")
        if not api_key:
            raise ValueError("❌ No se encontró GEMINI_API_KEY en el archivo .env")

        # Configurar SDK actualizado
        genai.configure(api_key=api_key)

        # ✅ Modelo actualizado a Gemini 2.5
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Modelo Gemini 2.5 Flash inicializado correctamente")

    def generate_response(self, message: str) -> str:
        try:
            response = self.model.generate_content(message)
            return response.text

        except Exception as e:
            print("❌ Error en Gemini:", e)
            return "Hubo un problema procesando tu solicitud. Intenta nuevamente."