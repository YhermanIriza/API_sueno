import pytest


class TestAuthentication:
    """
    Pruebas de autenticación: Login, registro, recuperación de contraseña.
    """

    def test_health_check(self, client):
        """
        Prueba que la API esté funcionando.
        """
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_login_success(self, client):
        """
        Prueba de login exitoso con credenciales válidas.
        """
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123",
            "recaptcha_token": "test_token_bypass"
        })
        
        # 💡 SUGERENCIA: Debería ser estrictamente 200 si el entorno de prueba está bien configurado.
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "role" in data

    def test_login_invalid_email(self, client):
        """
        Prueba de login con email que no existe.
        """
        response = client.post("/api/auth/login", json={
            "email": "noexiste@test.com",
            "password": "wrongpassword",
            "recaptcha_token": "test_token_bypass"
        })
        
        # 💡 SUGERENCIA: El servicio devuelve 401 para credenciales incorrectas.
        assert response.status_code == 401

    def test_login_invalid_password(self, client):
        """
        Prueba de login con contraseña incorrecta.
        """
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "wrongpassword",
            "recaptcha_token": "test_token_bypass"
        })
        
        # 💡 SUGERENCIA: El servicio devuelve 401 para credenciales incorrectas.
        assert response.status_code == 401

    def test_login_missing_recaptcha(self, client):
        """
        Prueba de login sin token de reCAPTCHA.
        """
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        
        # Debería fallar por falta de recaptcha_token
        assert response.status_code == 422  # Validation error

    def test_register_without_admin_token(self, client):
        """
        Prueba de registro sin ser admin (debería fallar).
        """
        response = client.post("/api/auth/register", json={
            "email": "nuevo@test.com",
            "password": "123456",
            "full_name": "Test User",
            "role_id": 2,
            "recaptcha_token": "test_token_bypass"
        })
        
        # Sin token de admin, debería retornar 401 o 403
        # 💡 SUGERENCIA: Sin token, FastAPI devuelve 401 (Unauthorized).
        assert response.status_code == 401

    def test_forgot_password(self, client):
        """
        Prueba de solicitud de recuperación de contraseña.
        """
        response = client.post("/api/auth/forgot-password", json={
            "email": "admin@test.com",
            "recaptcha_token": "test_token_bypass"
        })
        
        # 💡 SUGERENCIA: Para un email existente, esperamos 200.
        assert response.status_code == 200

    def test_reset_password_invalid_code(self, client):
        """
        Prueba de reset de contraseña con código inválido.
        """
        response = client.post("/api/auth/reset-password", json={
            "email": "admin@test.com",
            "code": "AAAAAA",  # Código de 6 caracteres válido pero incorrecto
            "new_password": "newpass123"
        })
        
        # 💡 SUGERENCIA: El servicio devuelve 400 para código incorrecto o expirado.
        assert response.status_code == 400