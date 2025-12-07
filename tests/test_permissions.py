import pytest


class TestRBACPermissions:
    """
    Pruebas de permisos basados en roles (RBAC).
    Verifica que los usuarios solo puedan acceder a recursos según su rol.
    """

    def test_user_cannot_list_users(self, client, user_headers):
        """
        Un usuario regular NO debería poder listar todos los usuarios.
        """
        if not user_headers:
            pytest.skip("No se pudo obtener token de usuario")
        
        response = client.get("/api/users", headers=user_headers)
        
        # Debería ser 403 (prohibido) porque no es admin
        assert response.status_code == 403

    def test_user_cannot_create_users(self, client, user_headers):
        """
        Un usuario regular NO debería poder crear nuevos usuarios.
        """
        if not user_headers:
            pytest.skip("No se pudo obtener token de usuario")
        
        response = client.post("/api/users", json={
            "email": "forbidden@test.com",
            "password": "123456",
            "full_name": "Forbidden User",
            "role_id": 2
        }, headers=user_headers)
        
        # Debería ser 403 (prohibido)
        assert response.status_code == 403

    def test_user_cannot_delete_users(self, client, user_headers):
        """
        Un usuario regular NO debería poder eliminar usuarios.
        """
        if not user_headers:
            pytest.skip("No se pudo obtener token de usuario")
        
        response = client.delete("/api/users/1", headers=user_headers)
        
        # Debería ser 403 (prohibido)
        assert response.status_code == 403

    def test_user_can_access_own_profile(self, client, user_headers):
        """
        Un usuario regular SÍ debería poder acceder a su propio perfil.
        """
        if not user_headers:
            pytest.skip("No se pudo obtener token de usuario")
        
        response = client.get("/api/me", headers=user_headers)
        
        # Debería ser 200 (permitido)
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "email" in data
            # Verificar que NO es admin
            assert data.get("role") != "admin"

    def test_admin_can_list_users(self, client, admin_headers):
        """
        Un admin SÍ debería poder listar todos los usuarios.
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        response = client.get("/api/users", headers=admin_headers)
        
        # Debería ser 200 (permitido)
        assert response.status_code == 200

    def test_admin_can_create_users(self, client, admin_headers):
        """
        Un admin SÍ debería poder crear nuevos usuarios.
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        response = client.post("/api/users", json={
            "email": f"admin_created_{pytest.__version__}@test.com",
            "password": "123456",
            "full_name": "Admin Created User",
            "role_id": 2
        }, headers=admin_headers)
        
        # Debería ser 200 (creado) o 400 (ya existe)
        assert response.status_code in [200, 400]

    def test_admin_can_access_profile(self, client, admin_headers):
        """
        Un admin SÍ debería poder acceder a su perfil.
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        response = client.get("/api/me", headers=admin_headers)
        
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "email" in data
            # Verificar que es admin
            assert data.get("role") == "admin"

    def test_invalid_token_rejected(self, client):
        """
        Un token inválido debería ser rechazado.
        """
        fake_headers = {"Authorization": "Bearer fake_invalid_token_12345"}
        
        response = client.get("/api/users", headers=fake_headers)
        
        # Debería ser 401 (no autorizado)
        assert response.status_code == 401

    def test_expired_token_rejected(self, client):
        """
        Un token expirado debería ser rechazado.
        """
        # Token JWT expirado (puedes generar uno que expire inmediatamente)
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.invalid"
        expired_headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/users", headers=expired_headers)
        
        # Debería ser 401 (no autorizado)
        assert response.status_code == 401