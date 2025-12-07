import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """
    Cliente de pruebas para hacer requests a la API.
    """
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token(client):
    """
    Obtiene un token de administrador para pruebas.
    NOTA: Asegúrate de tener un usuario admin en tu base de datos.
    Email: admin@test.com
    Password: admin123
    """
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123",
        "recaptcha_token": "test_token_bypass"
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # Si falla, retorna None (las pruebas manejarán esto)
    return None


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """
    Headers con token de administrador.
    """
    if admin_token:
        return {"Authorization": f"Bearer {admin_token}"}
    return {}


@pytest.fixture(scope="module")
def user_token(client):
    """
    Obtiene un token de usuario regular para pruebas.
    NOTA: Asegúrate de tener un usuario regular en tu base de datos.
    Email: user@test.com
    Password: user123
    """
    response = client.post("/api/auth/login", json={
        "email": "user@test.com",
        "password": "user123",
        "recaptcha_token": "test_token_bypass"
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    return None


@pytest.fixture(scope="module")
def user_headers(user_token):
    """
    Headers con token de usuario regular.
    """
    if user_token:
        return {"Authorization": f"Bearer {user_token}"}
    return {}