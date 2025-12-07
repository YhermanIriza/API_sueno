from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List

from app.core.security import decode_access_token

bearer_scheme = HTTPBearer()


class RBACMiddleware(BaseHTTPMiddleware):
    """
    Middleware para validar roles en rutas protegidas.
    Las rutas podrán definir los roles permitidos usando:
        request.state.allowed_roles = ["admin", "user"]
    """

    async def dispatch(self, request: Request, call_next):
        allowed_roles: List[str] = getattr(request.state, "allowed_roles", None)

        # Si la ruta no requiere roles → continuar
        if not allowed_roles:
            return await call_next(request)

        # Intentar obtener token
        try:
            credentials: HTTPAuthorizationCredentials = await bearer_scheme(request)
            token = credentials.credentials
        except Exception:
            raise HTTPException(status_code=401, detail="Token no proporcionado")

        # Decodificar y validar token
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")

        user_role = payload.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para acceder a esta ruta"
            )

        return await call_next(request)
