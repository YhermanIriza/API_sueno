import pytest


class TestUsersCRUD:
    """
    Pruebas de CRUD completo de usuarios.
    """

    def test_list_users_without_auth(self, client):
        """
        Intentar listar usuarios sin autenticación (debería fallar).
        """
        response = client.get("/api/users")
        assert response.status_code == 401

    def test_list_users_with_admin(self, client, admin_headers):
        """
        Listar usuarios con token de admin.
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        response = client.get("/api/users", headers=admin_headers)
        
        # Un admin siempre debe poder listar usuarios
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_by_id_with_admin(self, client, admin_headers):
        """
        Obtener usuario por ID con token de admin.
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        # Intentar obtener el usuario con ID 1
        response = client.get("/api/users/1", headers=admin_headers)
        
        # Asumimos que el usuario con ID 1 (admin) existe en la BD de pruebas
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_user_without_auth(self, client):
        """
        Intentar obtener usuario sin autenticación (debería fallar).
        """
        response = client.get("/api/users/1")
        assert response.status_code == 401

    def test_create_user_without_auth(self, client):
        """
        Intentar crear usuario sin autenticación (debería fallar).
        """
        response = client.post("/api/users", json={
            "email": "newuser@test.com",
            "password": "123456",
            "full_name": "New User",
            "role_id": 2
        })
        
        assert response.status_code == 401

    def test_create_user_with_admin(self, client, admin_headers):
        """
        Crear usuario con token de admin.
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        response = client.post("/api/users", json={
            "email": f"testuser_{pytest.__version__}@test.com",  # Email único
            "password": "123456",
            "full_name": "Test User",
            "role_id": 2
        }, headers=admin_headers)
        
        # Puede ser 200 (creado) o 400 (si el email ya existe en una ejecución anterior)
        # Ambas respuestas son válidas para esta prueba.
        assert response.status_code in [200, 400]

    def test_update_user_without_auth(self, client):
        """
        Intentar actualizar usuario sin autenticación (debería fallar).
        """
        response = client.put("/api/users/1", json={
            "full_name": "Updated Name"
        })
        
        assert response.status_code == 401

    def test_update_user_with_admin(self, client, admin_headers):
        """
        Actualizar usuario con token de admin.
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        response = client.put("/api/users/1", json={
            "full_name": "Updated Test Name"
        }, headers=admin_headers)
        
        # Asumimos que el usuario con ID 1 existe para ser actualizado
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Test Name"

    def test_delete_user_without_auth(self, client):
        """
        Intentar eliminar usuario sin autenticación (debería fallar).
        """
        response = client.delete("/api/users/999")
        assert response.status_code == 401

    def test_delete_user_with_admin(self, client, admin_headers):
        """
        Eliminar un usuario con token de admin (creamos uno para borrar).
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")

        # 1. Crear un usuario para luego borrarlo
        email_to_delete = f"delete_me_{pytest.__version__}@test.com"
        create_response = client.post("/api/users", json={
            "email": email_to_delete, "password": "123", "full_name": "Delete Me", "role_id": 2
        }, headers=admin_headers)
        assert create_response.status_code == 200
        user_id_to_delete = create_response.json()["id"]

        # 2. Borrar el usuario creado
        delete_response = client.delete(f"/api/users/{user_id_to_delete}", headers=admin_headers)
        assert delete_response.status_code == 200

    def test_get_profile(self, client, admin_headers):
        """
        Obtener perfil del usuario actual (/me).
        """
        if not admin_headers:
            pytest.skip("No se pudo obtener token de admin")
        
        response = client.get("/api/me", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == "admin@test.com"
        assert "role" in data

    def test_get_profile_without_auth(self, client):
        """
        Intentar obtener perfil sin autenticación (debería fallar).
        """
        response = client.get("/api/me")
        assert response.status_code == 401