import httpx
from fastapi import HTTPException
from app.core.config import settings

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify_recaptcha(token: str) -> bool:
    """
    Valida el token de reCAPTCHA v2 enviado desde el frontend.
    Lanza HTTPException si la verificación falla.
    """
    
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Token de reCAPTCHA requerido"
        )
    
    # MODO TESTING: Si el token es "test_token_bypass", permitir acceso
    if token == "test_token_bypass":
        print("⚠️ TESTING MODE: reCAPTCHA bypass activado")
        return True
    
    # Si no hay secret key configurada (desarrollo), permitir el acceso con advertencia
    if not settings.RECAPTCHA_SECRET_KEY or settings.RECAPTCHA_SECRET_KEY == "":
        print("⚠️ ADVERTENCIA: reCAPTCHA no configurado. Verificación omitida (solo desarrollo).")
        return True

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token
                },
                timeout=10.0
            )

        result = response.json()
        
        if not result.get("success", False):
            error_codes = result.get("error-codes", [])
            raise HTTPException(
                status_code=400,
                detail=f"Verificación de reCAPTCHA fallida: {', '.join(error_codes)}"
            )
        
        return True

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=500,
            detail="Timeout al verificar reCAPTCHA. Intenta de nuevo."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión con reCAPTCHA: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Error validando reCAPTCHA: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al validar reCAPTCHA"
        )