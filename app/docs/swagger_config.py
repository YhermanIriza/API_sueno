from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI):
    """
    Configuración avanzada y personalizada para Swagger UI y OpenAPI.
    """

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Backend API - Documentación Oficial",
        version="1.0.0",
        description="""
        Documentación oficial del API.  
        Aquí puedes revisar endpoints, modelos, parámetros, seguridad JWT y respuestas estándar.
        """,
        routes=app.routes,
    )

    # Información adicional
    openapi_schema["info"]["contact"] = {
        "name": "Soporte Técnico",
        "email": "support@midominio.com",
        "url": "https://midominio.com",
    }

    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }

    # Logo personalizado (opcional)
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "backgroundColor": "#FFFFFF",
        "altText": "API Logo"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_swagger(app: FastAPI):
    """
    Hook para aplicar la configuración personalizada al iniciar el servidor.
    """
    app.openapi = lambda: custom_openapi(app)
