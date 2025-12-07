from fastapi import HTTPException, status, Request
from time import time

# Estructura:
# {
#    "127.0.0.1:/login": [timestamps...]
# }
RATE_LIMIT_STORAGE = {}

DEFAULT_LIMIT = 5           # Máximo de intentos
DEFAULT_WINDOW = 60         # Ventana de tiempo: 60 segundos


def rate_limiter(route_id: str, limit: int = DEFAULT_LIMIT, window: int = DEFAULT_WINDOW):
    """
    Devuelve una función de dependencia para limitar peticiones por IP.
    route_id identifica el endpoint, ej: "login", "register".
    """
    async def limiter(request: Request):
        ip = request.client.host
        key = f"{ip}:{route_id}"

        now = time()
        requests_list = RATE_LIMIT_STORAGE.get(key, [])

        # Conservar solo las solicitudes dentro de la ventana
        requests_list = [ts for ts in requests_list if now - ts < window]

        if len(requests_list) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Demasiados intentos. Intenta de nuevo en unos segundos."
            )

        # Guardar timestamp actual
        requests_list.append(now)
        RATE_LIMIT_STORAGE[key] = requests_list

    return limiter
