# 🧠 Backend API - Higiene del Sueño y Control Digital

API robusta y segura construida con **FastAPI** para gestionar usuarios, roles y proporcionar análisis sobre hábitos digitales. Este backend sirve como soporte para la aplicación "Sueño App" y cumple con altos estándares de seguridad y buenas prácticas de desarrollo.

## ✨ Características Principales

### 🔒 Seguridad Nivel SENA
- **Autenticación JWT**: Sistema de tokens de acceso y refresco.
- **Roles y Permisos (RBAC)**: Rutas protegidas por roles (`admin`, `usuario`) usando dependencias de FastAPI.
- **Rate Limiting**: Limitación de peticiones en rutas sensibles (login, registro) para prevenir ataques de fuerza bruta.
- **CORS Seguro**: Configuración de `CORSMiddleware` para permitir solo orígenes específicos.
- **reCAPTCHA v2**: Validación en el backend para endpoints de autenticación.
- **Recuperación de Contraseña**: Flujo completo y seguro para restablecer la contraseña vía email.
- **Hashing de Contraseñas**: Uso de **bcrypt** para almacenar las contraseñas de forma segura.
- **Variables de Entorno**: Gestión centralizada y segura de secretos con Pydantic y archivos `.env`.

### 🛠️ Backend Robusto y Documentado
- **Arquitectura por Capas**: Código organizado, modular y escalable (capas de `api`, `services`, `core`, `db`).
- **Validación de Datos**: Uso intensivo de Pydantic para validar, serializar y documentar los modelos de datos.
- **Documentación Automática**: Endpoints de Swagger UI (`/docs`) y ReDoc (`/redoc`) generados automáticamente.
- **Pruebas Completas**: Cobertura de pruebas con `pytest` para el CRUD de usuarios, autenticación y lógica de permisos.

### 🗃️ Base de Datos
- **Integración con Supabase**: Conexión y gestión de una base de datos PostgreSQL a través del cliente de Supabase.
- **Script de Semilla (Seed)**: Script para inicializar la base de datos con roles (`admin`, `usuario`) y usuarios de prueba/demostración.

## 💻 Stack Tecnológico

- **Framework**: FastAPI
- **Servidor ASGI**: Uvicorn
- **Base de Datos**: Supabase (PostgreSQL)
- **Validación**: Pydantic
- **Seguridad**: Passlib[bcrypt], python-jose[cryptography], PyJWT
- **Pruebas**: Pytest, pytest-cov
- **Variables de Entorno**: python-dotenv, pydantic-settings

## ⚙️ Configuración del Entorno

1.  Crea un archivo `.env` en la raíz del proyecto.
2.  Copia el contenido de `.env.example` y rellena las variables.

```.env.example
# App
APP_NAME="Backend API - Sueño App"
APP_VERSION="1.0.0"

# JWT
SECRET_KEY="TU_SECRET_KEY_SUPER_SEGURO_DE_32_CARACTERES_O_MAS"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Supabase
SUPABASE_URL="https://tu-proyecto.supabase.co"
SUPABASE_KEY="tu_supabase_service_role_key"
SUPABASE_ANON_KEY="tu_supabase_anon_key"

# Email (para recuperación de contraseña)
EMAIL_FROM="tu-correo@gmail.com"
EMAIL_PASSWORD="tu_contraseña_de_aplicacion_de_gmail"

# reCAPTCHA
RECAPTCHA_SECRET_KEY="tu_secret_key_de_recaptcha_v2"
```

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

```bash
uvicorn app.main:app --reload
```

## 🧩 Estructura

- `api/`: Endpoints y lógica del negocio
- `core/`: Configuración, utilidades, base de datos
- `tests/`: Pruebas unitarias
